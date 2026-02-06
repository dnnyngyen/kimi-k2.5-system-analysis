# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
business_rules.py - Business rule validation (not covered by OpenXML SDK)

Checks:
  - gridCol/tcW width consistency (table not skewed)
  - Image cx/cy proportional scaling (not distorted)
  - Comments 4-file sync integrity
  - tblGrid existence
"""

import struct
from pathlib import Path
from xml.etree import ElementTree as ET

from .constants import W_NS, W14_NS, R_NS, WP_NS, A_NS


def check_table_grid_consistency(root):
    """Check table gridCol and tcW width consistency.

    Args:
        root: ElementTree root of document.xml

    Returns:
        List of error strings
    """
    errors = []
    tables = root.findall('.//{%s}tbl' % W_NS)

    for tbl_idx, tbl in enumerate(tables, 1):
        tbl_grid = tbl.find('{%s}tblGrid' % W_NS)
        if tbl_grid is None:
            errors.append(f"TABLE[{tbl_idx}]: missing tblGrid (required for proper rendering)")
            continue

        grid_cols = tbl_grid.findall('{%s}gridCol' % W_NS)
        grid_widths = []
        for gc in grid_cols:
            w_val = gc.get('{%s}w' % W_NS)
            grid_widths.append(int(w_val) if w_val else None)

        first_row = tbl.find('{%s}tr' % W_NS)
        if first_row is None:
            continue

        cells = first_row.findall('{%s}tc' % W_NS)
        for col_idx, (cell, grid_w) in enumerate(zip(cells, grid_widths)):
            tc_pr = cell.find('{%s}tcPr' % W_NS)
            if tc_pr is None:
                continue

            tc_w = tc_pr.find('{%s}tcW' % W_NS)
            if tc_w is None:
                continue

            tc_width = tc_w.get('{%s}w' % W_NS)
            if tc_width and grid_w:
                tc_width_int = int(tc_width)
                if abs(tc_width_int - grid_w) > grid_w * 0.05:
                    errors.append(
                        f"TABLE[{tbl_idx}]: gridCol[{col_idx}].w={grid_w} != tc[{col_idx}].tcW={tc_width_int} (will skew)"
                    )

    return errors


def get_image_dimensions(data):
    """Read actual image dimensions from binary data (supports PNG/JPEG).

    Args:
        data: bytes - Raw image file data

    Returns:
        Tuple (width, height) or (None, None) if unable to parse
    """
    try:
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            width, height = struct.unpack('>II', data[16:24])
            return width, height

        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data) - 9:
                if data[i] == 0xff:
                    marker = data[i+1]
                    if marker in (0xc0, 0xc2):
                        height, width = struct.unpack('>HH', data[i+5:i+9])
                        return width, height
                    elif marker == 0xd9:
                        break
                    elif marker in (0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0x01, 0x00):
                        i += 2
                    else:
                        length = struct.unpack('>H', data[i+2:i+4])[0]
                        i += 2 + length
                else:
                    i += 1
    except Exception:
        pass
    return None, None


def check_image_aspect_ratio(root, extract_dir):
    """Check if image display dimensions match actual image file aspect ratio.

    Args:
        root: ElementTree root of document.xml
        extract_dir: Path to extracted docx directory

    Returns:
        List of error strings
    """
    errors = []
    extract_dir = Path(extract_dir)

    # Parse document.xml.rels
    rels_map = {}
    rels_path = extract_dir / 'word' / '_rels' / 'document.xml.rels'
    if rels_path.exists():
        rels_tree = ET.parse(rels_path)
        rels_root = rels_tree.getroot()
        for rel in rels_root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            rid = rel.get('Id')
            target = rel.get('Target')
            if rid and target:
                if not target.startswith('/'):
                    target = 'word/' + target
                else:
                    target = target[1:]
                rels_map[rid] = target

    drawings = root.findall('.//{%s}drawing' % W_NS)

    for img_idx, drawing in enumerate(drawings, 1):
        extent = drawing.find('.//{%s}extent' % WP_NS)
        if extent is None:
            continue

        cx = extent.get('cx')
        cy = extent.get('cy')
        if not cx or not cy:
            continue

        cx_val = int(cx)
        cy_val = int(cy)
        if cy_val == 0:
            continue

        display_ratio = cx_val / cy_val

        blip = drawing.find('.//{%s}blip' % A_NS)
        if blip is None:
            continue

        embed_id = blip.get('{%s}embed' % R_NS)
        if not embed_id or embed_id not in rels_map:
            continue

        image_path = extract_dir / rels_map[embed_id]
        if not image_path.exists():
            continue

        data = image_path.read_bytes()
        actual_width, actual_height = get_image_dimensions(data)
        if actual_width is None or actual_height is None or actual_height == 0:
            continue

        actual_ratio = actual_width / actual_height

        if abs(display_ratio - actual_ratio) / actual_ratio > 0.05:
            filename = image_path.name
            errors.append(
                f"IMAGE[{img_idx}] {filename}: display={display_ratio:.2f} != actual={actual_ratio:.2f} (distorted)"
            )

    return errors


def check_comments_integrity(extract_dir):
    """Check comments 4-file sync integrity.

    Args:
        extract_dir: Path to extracted docx directory

    Returns:
        List of error strings
    """
    errors = []
    extract_dir = Path(extract_dir)

    has_comments = (extract_dir / 'word' / 'comments.xml').exists()
    has_comments_extended = (extract_dir / 'word' / 'commentsExtended.xml').exists()
    has_comments_ids = (extract_dir / 'word' / 'commentsIds.xml').exists()

    if has_comments:
        comments_tree = ET.parse(extract_dir / 'word' / 'comments.xml')
        comments_root = comments_tree.getroot()
        comments = comments_root.findall('.//{%s}comment' % W_NS)

        has_replies = False
        for comment in comments:
            para = comment.find('{%s}p' % W_NS)
            if para is not None:
                para_id = para.get('{%s}paraId' % W14_NS)
                if para_id:
                    has_replies = True
                    break

        if has_replies:
            if not has_comments_extended:
                errors.append("COMMENTS: has threaded replies but missing commentsExtended.xml")
            if not has_comments_ids:
                errors.append("COMMENTS: has threaded replies but missing commentsIds.xml")

    return errors


def check_section_margins(root):
    """Check section margins for potential issues.

    Detects:
    - Zero margins on non-cover/backcover sections (likely bug)
    - Last section with zero margins affecting body content

    Args:
        root: ElementTree root of document.xml

    Returns:
        List of warning strings
    """
    warnings = []

    # Find all sectPr elements
    # sectPr can be in: body > sectPr (last section) or p > pPr > sectPr (section breaks)
    body = root.find('.//{%s}body' % W_NS)
    if body is None:
        return warnings

    sections = []

    # Section breaks within paragraphs
    for para in body.findall('.//{%s}p' % W_NS):
        pPr = para.find('{%s}pPr' % W_NS)
        if pPr is not None:
            sectPr = pPr.find('{%s}sectPr' % W_NS)
            if sectPr is not None:
                sections.append(('inline', sectPr))

    # Final section at body end
    final_sectPr = body.find('{%s}sectPr' % W_NS)
    if final_sectPr is not None:
        sections.append(('final', final_sectPr))

    if len(sections) < 2:
        # Single section document, no issue
        return warnings

    # Check each section's margins
    MIN_MARGIN_TWIPS = 360  # 0.25 inch minimum for body content

    for idx, (sect_type, sectPr) in enumerate(sections):
        pgMar = sectPr.find('{%s}pgMar' % W_NS)
        if pgMar is None:
            continue

        # Get margin values
        margins = {
            'top': pgMar.get('{%s}top' % W_NS, '1440'),
            'bottom': pgMar.get('{%s}bottom' % W_NS, '1440'),
            'left': pgMar.get('{%s}left' % W_NS, '1440'),
            'right': pgMar.get('{%s}right' % W_NS, '1440'),
        }

        # Convert to int, handle negative values
        try:
            margin_values = {k: abs(int(v)) for k, v in margins.items()}
        except ValueError:
            continue

        # Check if all margins are zero or very small
        all_zero = all(v < MIN_MARGIN_TWIPS for v in margin_values.values())

        if all_zero:
            # First section (cover) and last section (backcover) can have zero margins
            is_first = (idx == 0)
            is_last = (idx == len(sections) - 1 and sect_type == 'final')

            if is_last and len(sections) > 2:
                # Final section with zero margins might affect preceding content
                # if there are sections between first and last without their own sectPr
                warnings.append(
                    f"MARGIN: final section has zero margins - may affect body content if intermediate sections lack sectPr"
                )
            elif not is_first and not is_last:
                # Middle section with zero margins is likely a bug
                warnings.append(
                    f"MARGIN: section[{idx+1}] has zero margins (top={margin_values['top']}, left={margin_values['left']}) - body content may touch page edges"
                )

    return warnings
