#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
fix_element_order.py - Auto-fix OpenXML element ordering issues in docx files

Usage: python fix_element_order.py <file.docx>

Fixes known element order violations that cause OpenXML validation to fail:
  - rPr: rFonts -> b -> i -> color -> sz -> szCs -> u
  - pPr: pStyle -> pBdr -> shd -> tabs -> spacing -> ind -> jc
  - sectPr: headerReference -> footerReference -> type -> pgSz -> pgMar -> titlePg
  - tcPr: tcW -> tcBorders -> shd -> vAlign
  - tblPr: tblW -> tblBorders -> tblLayout
  - tblBorders: top -> left -> bottom -> right -> insideH -> insideV
  - Level: start -> numFmt -> lvlText -> pPr

This script modifies the docx file IN PLACE.
"""

import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET

# Import from shared library
from docx_lib import fix_element_order_in_tree, fix_settings


def fix_docx(docx_path):
    """Fix element order issues in a docx file. Modifies in place."""
    docx_path = Path(docx_path)

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        return False

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        extract_dir = tmpdir / 'extracted'

        # Extract docx
        try:
            with zipfile.ZipFile(docx_path, 'r') as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            print(f"Error: Invalid docx file: {docx_path}")
            return False

        total_fixes = 0

        # Fix document.xml
        doc_xml = extract_dir / 'word' / 'document.xml'
        if doc_xml.exists():
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            fixes = fix_element_order_in_tree(root)
            if fixes > 0:
                tree.write(doc_xml, encoding='UTF-8', xml_declaration=True)
                total_fixes += fixes

        # Fix styles.xml
        styles_xml = extract_dir / 'word' / 'styles.xml'
        if styles_xml.exists():
            tree = ET.parse(styles_xml)
            root = tree.getroot()
            fixes = fix_element_order_in_tree(root)
            if fixes > 0:
                tree.write(styles_xml, encoding='UTF-8', xml_declaration=True)
                total_fixes += fixes

        # Fix numbering.xml
        numbering_xml = extract_dir / 'word' / 'numbering.xml'
        if numbering_xml.exists():
            tree = ET.parse(numbering_xml)
            root = tree.getroot()
            fixes = fix_element_order_in_tree(root)
            if fixes > 0:
                tree.write(numbering_xml, encoding='UTF-8', xml_declaration=True)
                total_fixes += fixes

        # Fix settings.xml
        settings_xml = extract_dir / 'word' / 'settings.xml'
        if settings_xml.exists():
            tree = ET.parse(settings_xml)
            root = tree.getroot()
            fixes = fix_settings(root)
            fixes += fix_element_order_in_tree(root)
            if fixes > 0:
                tree.write(settings_xml, encoding='UTF-8', xml_declaration=True)
                total_fixes += fixes

        # Fix header/footer files
        for xml_file in (extract_dir / 'word').glob('header*.xml'):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            fixes = fix_element_order_in_tree(root)
            if fixes > 0:
                tree.write(xml_file, encoding='UTF-8', xml_declaration=True)
                total_fixes += fixes

        for xml_file in (extract_dir / 'word').glob('footer*.xml'):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            fixes = fix_element_order_in_tree(root)
            if fixes > 0:
                tree.write(xml_file, encoding='UTF-8', xml_declaration=True)
                total_fixes += fixes

        if total_fixes == 0:
            # Silent when nothing to fix
            return True

        # Repack docx with correct file order
        # [Content_Types].xml must be first, then _rels/, then others
        backup_path = docx_path.with_suffix('.docx.bak')
        shutil.copy2(docx_path, backup_path)

        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            all_files = list(extract_dir.rglob('*'))
            all_files = [f for f in all_files if f.is_file()]

            # Sort: [Content_Types].xml first, _rels second, others after
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

        # Remove backup if successful
        backup_path.unlink()

        print(f"Fixed {total_fixes} element order issues")
        return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    docx_path = sys.argv[1]

    if fix_docx(docx_path):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
