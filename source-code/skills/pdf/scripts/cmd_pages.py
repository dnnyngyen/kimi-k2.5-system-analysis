# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""Page operation commands"""

import pikepdf
from pathlib import Path
from pdf import Output


def _parse_pages(pages_str: str, total: int) -> list:
    """Parse page range string, returns 0-indexed list"""
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


def pages_merge(pdf_paths: list, output_path: str):
    """Merge multiple PDFs"""
    # Validate all files exist
    paths = []
    for p in pdf_paths:
        path = Output.check_file(p)
        paths.append(path)

    opened_pdfs = []  # Track opened PDFs for cleanup
    try:
        output_pdf = pikepdf.new()
        sources = []

        for path in paths:
            src = pikepdf.open(path)
            opened_pdfs.append(src)  # Track for cleanup
            page_count = len(src.pages)
            sources.append(f"{path.name} ({page_count} pages)")

            for page in src.pages:
                output_pdf.pages.append(page)

        total_pages = len(output_pdf.pages)
        output_pdf.save(output_path)
        output_pdf.close()

        # Close all source PDFs
        for src in opened_pdfs:
            src.close()

    except Exception as e:
        # Cleanup on error
        for src in opened_pdfs:
            try:
                src.close()
            except:
                pass
        Output.error("MergeError", f"Merge failed: {e}", code=4)

    Output.success({
        "output": output_path,
        "total_pages": total_pages,
        "sources": sources
    })


def pages_split(pdf_path: str, output_dir: str):
    """Split PDF into single-page files"""
    path = Output.check_file(pdf_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    stem = path.stem
    outputs = []

    try:
        for i, page in enumerate(pdf.pages, 1):
            out_path = out_dir / f"{stem}_page{i:03d}.pdf"
            single = pikepdf.new()
            single.pages.append(page)
            single.save(out_path)
            single.close()
            outputs.append(str(out_path))

        pdf.close()

    except Exception as e:
        Output.error("SplitError", f"Split failed: {e}", code=4)

    Output.success({
        "output_dir": str(out_dir),
        "total_pages": len(outputs),
        "files": outputs
    })


def pages_rotate(pdf_path: str, degrees: int, output_path: str, pages: str = None):
    """Rotate pages"""
    path = Output.check_file(pdf_path)

    if degrees not in (90, 180, 270):
        Output.error("InvalidDegrees", "Rotation angle must be 90, 180, or 270")

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    page_indices = _parse_pages(pages, len(pdf.pages))

    try:
        for idx in page_indices:
            page = pdf.pages[idx]
            current = int(page.get("/Rotate", 0))
            page["/Rotate"] = (current + degrees) % 360

        pdf.save(output_path)
        pdf.close()

    except Exception as e:
        Output.error("RotateError", f"Rotation failed: {e}", code=4)

    Output.success({
        "output": output_path,
        "degrees": degrees,
        "pages_rotated": len(page_indices)
    })


def pages_crop(pdf_path: str, box: str, output_path: str, pages: str = None):
    """Crop pages

    box format: "left,bottom,right,top" (in pt)
    """
    path = Output.check_file(pdf_path)

    # Parse crop box
    try:
        parts = [float(x.strip()) for x in box.split(",")]
        if len(parts) != 4:
            raise ValueError()
        left, bottom, right, top = parts
    except:
        Output.error("InvalidBox", "Invalid crop box format, should be: left,bottom,right,top", hint="Example: 50,50,550,750")

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    page_indices = _parse_pages(pages, len(pdf.pages))

    try:
        for idx in page_indices:
            page = pdf.pages[idx]
            page.mediabox = pikepdf.Array([left, bottom, right, top])
            # Also set cropbox
            page.cropbox = pikepdf.Array([left, bottom, right, top])

        pdf.save(output_path)
        pdf.close()

    except Exception as e:
        Output.error("CropError", f"Crop failed: {e}", code=4)

    Output.success({
        "output": output_path,
        "box": {"left": left, "bottom": bottom, "right": right, "top": top},
        "pages_cropped": len(page_indices)
    })
