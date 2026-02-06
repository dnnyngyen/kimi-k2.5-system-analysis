#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
validate_all.py - Unified validation: element order fix + business rules check
One unzip, two checks

Usage: python validate_all.py <file.docx>

Combines:
  - fix_element_order: Auto-fix XML element ordering issues
  - validate_docx: Business rule validation (table grid, image aspect, comments)
"""

import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET

# Import from shared library
from docx_lib import (
    fix_element_order_in_tree,
    fix_settings,
    fix_table_width_conservative,
    check_table_grid_consistency,
    check_image_aspect_ratio,
    check_comments_integrity,
    check_section_margins,
)


def validate_and_fix(docx_path):
    """
    One unzip, two checks:
    1. Fix element order (modifies XML in place)
    2. Business rule validation (read-only)

    Returns: (fix_count, errors)
    """
    docx_path = Path(docx_path)

    if not docx_path.exists():
        return 0, [f"FILE: not found: {docx_path}"]

    with tempfile.TemporaryDirectory() as tmpdir:
        extract_dir = Path(tmpdir) / 'extracted'

        # 1. Unzip
        try:
            with zipfile.ZipFile(docx_path, 'r') as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            return 0, ["STRUCTURE: File corrupted or not valid docx"]

        total_fixes = 0
        errors = []

        # 2. Fix element order in XML files
        xml_files = [
            ('word/document.xml', False),
            ('word/styles.xml', False),
            ('word/numbering.xml', False),
            ('word/settings.xml', True),  # needs special handling
        ]

        for rel_path, is_settings in xml_files:
            xml_path = extract_dir / rel_path
            if xml_path.exists():
                tree = ET.parse(xml_path)
                root = tree.getroot()
                fixes = fix_element_order_in_tree(root)
                if is_settings:
                    fixes += fix_settings(root)
                # Fix table width consistency in document.xml
                if rel_path == 'word/document.xml':
                    fixes += fix_table_width_conservative(root)
                if fixes > 0:
                    tree.write(xml_path, encoding='UTF-8', xml_declaration=True)
                    total_fixes += fixes

        # Fix header/footer files
        word_dir = extract_dir / 'word'
        for xml_file in list(word_dir.glob('header*.xml')) + list(word_dir.glob('footer*.xml')):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            fixes = fix_element_order_in_tree(root)
            if fixes > 0:
                tree.write(xml_file, encoding='UTF-8', xml_declaration=True)
                total_fixes += fixes

        # 3. Business rule validation
        doc_xml = extract_dir / 'word' / 'document.xml'
        warnings = []
        if doc_xml.exists():
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            errors.extend(check_table_grid_consistency(root))
            errors.extend(check_image_aspect_ratio(root, extract_dir))
            warnings.extend(check_section_margins(root))

        errors.extend(check_comments_integrity(extract_dir))

        # 4. Repack if fixes were made
        if total_fixes > 0:
            # Repack with correct file order
            backup_path = docx_path.with_suffix('.docx.bak')
            shutil.copy2(docx_path, backup_path)

            with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                all_files = [f for f in extract_dir.rglob('*') if f.is_file()]

                def sort_key(f):
                    rel = str(f.relative_to(extract_dir))
                    if rel == '[Content_Types].xml':
                        return (0, rel)
                    elif rel.startswith('_rels'):
                        return (1, rel)
                    elif rel.startswith('word/_rels'):
                        return (2, rel)
                    else:
                        return (3, rel)

                for file_path in sorted(all_files, key=sort_key):
                    arcname = file_path.relative_to(extract_dir)
                    zf.write(file_path, arcname)

            backup_path.unlink()

        return total_fixes, errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_all.py <file.docx>")
        sys.exit(1)

    docx_path = sys.argv[1]

    fixes, errors, warnings = validate_and_fix(docx_path)

    if fixes > 0:
        print(f"Fixed {fixes} element order issues")

    for warn in warnings:
        print(f"Warning: {warn}")

    if errors:
        for err in errors:
            print(f"Error: {err}")
        sys.exit(1)
    else:
        print("Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
