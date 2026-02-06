# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""Metadata operation commands"""

import pikepdf
from datetime import datetime
from pdf import Output


def meta_get(pdf_path: str):
    """Read metadata"""
    path = Output.check_file(pdf_path)

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    # Basic info
    info = {
        "pages": len(pdf.pages),
        "pdf_version": str(pdf.pdf_version),
    }

    # Page size (first page)
    if pdf.pages:
        first_page = pdf.pages[0]
        mbox = first_page.mediabox
        info["page_size"] = {
            "width": float(mbox[2] - mbox[0]),
            "height": float(mbox[3] - mbox[1]),
            "unit": "pt"
        }

    # Document info dictionary
    metadata = {}
    if pdf.docinfo:
        for key in pdf.docinfo.keys():
            try:
                value = pdf.docinfo[key]
                # Convert to string
                if hasattr(value, "__str__"):
                    metadata[str(key).lstrip("/")] = str(value)
            except:
                pass

    info["metadata"] = metadata

    # Is encrypted
    info["encrypted"] = pdf.is_encrypted

    # Has form
    info["has_form"] = "/AcroForm" in pdf.Root

    # Has bookmarks
    info["has_outlines"] = "/Outlines" in pdf.Root

    pdf.close()

    Output.success(info)


def meta_set(pdf_path: str, output_path: str, data: dict):
    """Set metadata

    Supported fields:
    - Title: Document title
    - Author: Author name
    - Subject: Subject
    - Keywords: Keywords
    - Creator: Creator application
    - Producer: Producer application
    """
    path = Output.check_file(pdf_path)

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    # Allowed metadata fields
    allowed_keys = {"Title", "Author", "Subject", "Keywords", "Creator", "Producer"}

    # Create or update docinfo
    with pdf.open_metadata() as meta:
        # Use XMP metadata (more modern approach)
        updated = []
        for key, value in data.items():
            # Normalize key
            normalized_key = key.title()
            if normalized_key not in allowed_keys:
                continue

            # Map to XMP namespace
            xmp_map = {
                "Title": "dc:title",
                "Author": "dc:creator",
                "Subject": "dc:description",
                "Keywords": "pdf:Keywords",
                "Creator": "xmp:CreatorTool",
                "Producer": "pdf:Producer"
            }

            if normalized_key in xmp_map:
                try:
                    meta[xmp_map[normalized_key]] = str(value)
                    updated.append(normalized_key)
                except:
                    pass

    # Also update docinfo (for compatibility)
    if not pdf.docinfo:
        pdf.docinfo = pikepdf.Dictionary()

    for key, value in data.items():
        normalized_key = key.title()
        if normalized_key in allowed_keys:
            pdf.docinfo[pikepdf.Name(f"/{normalized_key}")] = pikepdf.String(str(value))

    # Update modification date
    now = datetime.now().strftime("D:%Y%m%d%H%M%S")
    pdf.docinfo[pikepdf.Name("/ModDate")] = pikepdf.String(now)

    try:
        pdf.save(output_path)
        pdf.close()
    except Exception as e:
        Output.error("SaveError", f"Save failed: {e}", code=4)

    Output.success({
        "output": output_path,
        "updated_fields": list(data.keys())
    })
