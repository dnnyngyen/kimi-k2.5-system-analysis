# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""Content extraction commands"""

import pdfplumber
import pikepdf
from pathlib import Path
from pdf import Output


def _parse_pages(pages_str: str, total: int) -> list:
    """Parse page range string

    Supported formats: "1", "1-3", "1,3,5", "1-3,5,7-9"
    Returns 0-indexed page number list
    """
    if not pages_str:
        return list(range(total))

    result = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start = int(start) - 1
            end = int(end)
            result.extend(range(start, min(end, total)))
        else:
            idx = int(part) - 1
            if 0 <= idx < total:
                result.append(idx)

    return sorted(set(result))


def extract_text(pdf_path: str, pages: str = None):
    """Extract text"""
    path = Output.check_file(pdf_path)

    try:
        pdf = pdfplumber.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    page_indices = _parse_pages(pages, len(pdf.pages))

    result = {
        "total_pages": len(pdf.pages),
        "extracted_pages": len(page_indices),
        "pages": []
    }

    total_chars = 0
    for idx in page_indices:
        page = pdf.pages[idx]
        text = page.extract_text() or ""
        total_chars += len(text)

        result["pages"].append({
            "page": idx + 1,
            "chars": len(text),
            "text": text
        })

    result["total_chars"] = total_chars
    pdf.close()

    Output.success(result)


def extract_table(pdf_path: str, pages: str = None):
    """Extract tables"""
    path = Output.check_file(pdf_path)

    try:
        pdf = pdfplumber.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    page_indices = _parse_pages(pages, len(pdf.pages))

    result = {
        "total_pages": len(pdf.pages),
        "extracted_pages": len(page_indices),
        "tables": []
    }

    for idx in page_indices:
        page = pdf.pages[idx]
        tables = page.extract_tables()

        for i, table in enumerate(tables):
            if not table:
                continue

            # Clean table data
            cleaned = []
            for row in table:
                cleaned_row = [cell.strip() if cell else "" for cell in row]
                cleaned.append(cleaned_row)

            result["tables"].append({
                "page": idx + 1,
                "table_index": i,
                "rows": len(cleaned),
                "cols": len(cleaned[0]) if cleaned else 0,
                "data": cleaned
            })

    result["total_tables"] = len(result["tables"])
    pdf.close()

    Output.success(result)


def extract_image(pdf_path: str, output_dir: str):
    """Extract embedded images"""
    path = Output.check_file(pdf_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    extracted = []
    image_count = 0

    for page_num, page in enumerate(pdf.pages, 1):
        # Get images from page resources
        if "/Resources" not in page:
            continue

        resources = page.Resources
        if "/XObject" not in resources:
            continue

        xobjects = resources.XObject
        for name, xobj in xobjects.items():
            if not hasattr(xobj, "objgen"):
                continue

            try:
                obj = pdf.get_object(xobj.objgen)
                if obj.get("/Subtype") != "/Image":
                    continue

                # Get image info
                width = int(obj.get("/Width", 0))
                height = int(obj.get("/Height", 0))
                color_space = str(obj.get("/ColorSpace", ""))
                bits = int(obj.get("/BitsPerComponent", 8))

                # Try to extract image data
                image_count += 1
                filter_type = obj.get("/Filter")

                # Determine file extension
                if filter_type == "/DCTDecode":
                    ext = "jpg"
                elif filter_type == "/FlateDecode":
                    ext = "png"
                elif filter_type == "/JPXDecode":
                    ext = "jp2"
                else:
                    ext = "bin"

                # Save image
                filename = f"page{page_num}_img{image_count}.{ext}"
                filepath = out_dir / filename

                try:
                    raw_data = obj.read_raw_bytes()
                    with open(filepath, "wb") as f:
                        f.write(raw_data)

                    extracted.append({
                        "page": page_num,
                        "name": str(name),
                        "file": str(filepath),
                        "width": width,
                        "height": height,
                        "format": ext
                    })
                except Exception:
                    # Some image formats cannot be directly extracted
                    pass

            except Exception:
                continue

    pdf.close()

    Output.success({
        "output_dir": str(out_dir),
        "total_images": len(extracted),
        "images": extracted
    })
