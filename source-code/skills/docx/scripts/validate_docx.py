#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
validate_docx.py - Custom business rule validation (not covered by OpenXML SDK)
Usage: python validate_docx.py <file.docx>

Checks (only what OpenXML SDK doesn't cover):
  - gridCol/tcW width consistency (table not skewed)
  - Image cx/cy proportional scaling (not distorted)
  - Comments 4-file sync integrity
  - tblGrid existence

Output format (high density, LLM-friendly):
  Error: TABLE[2]: gridCol[0].w=5000 != tc[0].tcW=4500
  Error: IMAGE[1]: aspect=1.60 != original=1.78 (will distort)
  Validation passed
"""

import sys
import zipfile
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

# Import from shared library
from docx_lib import (
    W_NS,
    check_table_grid_consistency,
    check_image_aspect_ratio,
    check_comments_integrity,
)


def check_document_settings(extract_dir):
    """Check document settings (like TOC update)"""
    errors = []
    warnings = []
    extract_dir = Path(extract_dir)

    settings_path = extract_dir / 'word' / 'settings.xml'
    if settings_path.exists():
        settings_tree = ET.parse(settings_path)
        settings_root = settings_tree.getroot()

        # Check updateFields (TOC auto-update)
        update_fields = settings_root.find('.//{%s}updateFields' % W_NS)

        # Check if there is TOC
        doc_path = extract_dir / 'word' / 'document.xml'
        if doc_path.exists():
            doc_tree = ET.parse(doc_path)
            doc_root = doc_tree.getroot()

            # Find TOC related field code
            field_codes = doc_root.findall('.//{%s}instrText' % W_NS)
            has_toc = any('TOC' in (fc.text or '') for fc in field_codes)

            if has_toc and update_fields is None:
                # This is a warning not error, TOC can be manually updated
                warnings.append(
                    "TOC: consider adding <w:updateFields w:val=\"true\"/> in settings.xml for auto-update"
                )

    return errors, warnings


def validate_document(docx_path):
    """Validate docx document"""
    errors = []
    warnings = []

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            extract_dir = Path(tmpdir) / 'extracted'

            # Extract docx
            with zipfile.ZipFile(docx_path, 'r') as zf:
                zf.extractall(extract_dir)

            # Check required files
            doc_path = extract_dir / 'word' / 'document.xml'
            if not doc_path.exists():
                errors.append("STRUCTURE: word/document.xml missing")
                return errors, warnings

            # Parse document.xml
            tree = ET.parse(doc_path)
            root = tree.getroot()

            # Business rule checks
            errors.extend(check_table_grid_consistency(root))
            errors.extend(check_image_aspect_ratio(root, extract_dir))
            errors.extend(check_comments_integrity(extract_dir))

            doc_errors, doc_warnings = check_document_settings(extract_dir)
            errors.extend(doc_errors)
            warnings.extend(doc_warnings)

    except zipfile.BadZipFile:
        errors.append("STRUCTURE: File corrupted or not valid docx")
    except Exception as e:
        errors.append(f"PARSE: {str(e)}")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_docx.py <file.docx>")
        sys.exit(1)

    docx_path = sys.argv[1]

    if not Path(docx_path).exists():
        print(f"Error: FILE: not found: {docx_path}")
        sys.exit(1)

    errors, warnings = validate_document(docx_path)

    # Output warnings
    for warn in warnings:
        print(f"Warning: {warn}")

    # Output errors
    if errors:
        for err in errors:
            print(f"Error: {err}")
        sys.exit(1)
    else:
        print("Custom validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
