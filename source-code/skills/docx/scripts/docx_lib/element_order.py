# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
element_order.py - Enhanced OpenXML element order definitions and fix functions

This is an enhanced version that fixes additional element order issues:
  - pBdr (paragraph borders): top -> left -> bottom -> right -> between -> bar
  - tcMar (table cell margins): top -> left -> bottom -> right -> start -> end
  - tblCellMar (table default margins): same as tcMar
  - numbering: abstractNum -> num
  - tr (table row): tblPrEx -> trPr -> tc
  - body: sectPr must be the last child element

Also adds:
  - wrap_border_elements: wraps misplaced border elements into pBdr/tcBorders
  - fix_body_order: ensures sectPr is the last child of body

Original element orders:
  - rPr: rFonts -> b -> i -> color -> sz -> szCs -> u -> rtl
  - pPr: pStyle -> pBdr -> shd -> tabs -> spacing -> ind -> jc
  - sectPr: headerReference -> footerReference -> type -> pgSz -> pgMar -> titlePg
  - tcPr: tcW -> tcBorders -> shd -> vAlign
  - tblPr: tblW -> tblBorders -> tblLayout
  - tblBorders/tcBorders: top -> left -> bottom -> right -> insideH -> insideV
  - Level: start -> numFmt -> lvlText -> pPr
"""

from .constants import w, W_NS

# ============================================================
# Original element order specifications
# ============================================================

RPR_ORDER = [
    'rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps',
    'strike', 'dstrike', 'outline', 'shadow', 'emboss', 'imprint',
    'noProof', 'snapToGrid', 'vanish', 'webHidden', 'color', 'spacing',
    'w', 'kern', 'position', 'sz', 'szCs', 'highlight', 'u', 'effect',
    'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang',
    'eastAsianLayout', 'specVanish', 'oMath'
]

PPR_ORDER = [
    'pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr',
    'widowControl', 'numPr', 'suppressLineNumbers', 'pBdr', 'shd',
    'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap',
    'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN',
    'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind',
    'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc',
    'textDirection', 'textAlignment', 'textboxTightWrap',
    'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange'
]

SECTPR_ORDER = [
    'headerReference', 'footerReference', 'footnotePr', 'endnotePr',
    'type', 'pgSz', 'pgMar', 'paperSrc', 'pgBorders', 'lnNumType',
    'pgNumType', 'cols', 'formProt', 'vAlign', 'noEndnote', 'titlePg',
    'textDirection', 'bidi', 'rtlGutter', 'docGrid', 'printerSettings',
    'sectPrChange'
]

TCPR_ORDER = [
    'cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders',
    'shd', 'noWrap', 'tcMar', 'textDirection', 'tcFitText', 'vAlign',
    'hideMark', 'headers', 'cellIns', 'cellDel', 'cellMerge', 'tcPrChange'
]

TBLPR_ORDER = [
    'tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize',
    'tblStyleColBandSize', 'tblW', 'jc', 'tblCellSpacing', 'tblInd',
    'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook', 'tblCaption',
    'tblDescription', 'tblPrChange'
]

TBLBORDERS_ORDER = [
    'top', 'left', 'bottom', 'right', 'insideH', 'insideV'
]

LEVEL_ORDER = [
    'start', 'numFmt', 'lvlRestart', 'pStyle', 'isLgl', 'suff',
    'lvlText', 'lvlPicBulletId', 'legacy', 'lvlJc', 'pPr', 'rPr'
]

SETTINGS_ORDER = [
    'writeProtection', 'view', 'zoom', 'removePersonalInformation',
    'removeDateAndTime', 'doNotDisplayPageBoundaries', 'displayBackgroundShape',
    'printPostScriptOverText', 'printFractionalCharacterWidth',
    'printFormsData', 'embedTrueTypeFonts', 'embedSystemFonts',
    'saveSubsetFonts', 'saveFormsData', 'mirrorMargins', 'alignBordersAndEdges',
    'bordersDoNotSurroundHeader', 'bordersDoNotSurroundFooter',
    'gutterAtTop', 'hideSpellingErrors', 'hideGrammaticalErrors',
    'activeWritingStyle', 'proofState', 'formsDesign', 'attachedTemplate',
    'linkStyles', 'stylePaneFormatFilter', 'stylePaneSortMethod',
    'documentType', 'mailMerge', 'revisionView', 'trackRevisions',
    'doNotTrackMoves', 'doNotTrackFormatting', 'documentProtection',
    'autoFormatOverride', 'styleLockTheme', 'styleLockQFSet',
    'defaultTabStop', 'autoHyphenation', 'consecutiveHyphenLimit',
    'hyphenationZone', 'doNotHyphenateCaps', 'showEnvelope', 'summaryLength',
    'clickAndTypeStyle', 'defaultTableStyle', 'evenAndOddHeaders',
    'bookFoldRevPrinting', 'bookFoldPrinting', 'bookFoldPrintingSheets',
    'drawingGridHorizontalSpacing', 'drawingGridVerticalSpacing',
    'displayHorizontalDrawingGridEvery', 'displayVerticalDrawingGridEvery',
    'doNotUseMarginsForDrawingGridOrigin', 'drawingGridHorizontalOrigin',
    'drawingGridVerticalOrigin', 'doNotShadeFormData', 'noPunctuationKerning',
    'characterSpacingControl', 'printTwoOnOne', 'strictFirstAndLastChars',
    'noLineBreaksAfter', 'noLineBreaksBefore', 'savePreviewPicture',
    'doNotValidateAgainstSchema', 'saveInvalidXml', 'ignoreMixedContent',
    'alwaysShowPlaceholderText', 'doNotDemarcateInvalidXml',
    'saveXmlDataOnly', 'useXSLTWhenSaving', 'saveThroughXslt',
    'showXMLTags', 'alwaysMergeEmptyNamespace', 'updateFields',
    'hdrShapeDefaults', 'footnotePr', 'endnotePr', 'compat', 'docVars',
    'rsids', 'mathPr', 'attachedSchema', 'themeFontLang', 'clrSchemeMapping',
    'doNotIncludeSubdocsInStats', 'doNotAutoCompressPictures',
    'forceUpgrade', 'captions', 'readModeInkLockDown', 'schemaLibrary',
    'shapeDefaults', 'doNotEmbedSmartTags', 'decimalSymbol', 'listSeparator'
]

# ============================================================
# NEW element order specifications (fixes ~93% of Schema errors)
# ============================================================

# Paragraph borders - fixes 190 errors
PBDR_ORDER = [
    'top', 'left', 'bottom', 'right', 'between', 'bar'
]

# Table cell margins - fixes 41 errors
TCMAR_ORDER = [
    'top', 'left', 'bottom', 'right', 'start', 'end'
]

# Table default cell margins - fixes 17 errors
TBLCELLMAR_ORDER = [
    'top', 'left', 'bottom', 'right', 'start', 'end'
]

# Numbering definitions - fixes 216 errors
NUMBERING_ORDER = [
    'abstractNum', 'num'
]

# Table row elements - fixes 3 errors
TR_ORDER = [
    'tblPrEx', 'trPr', 'tc', 'customXml', 'sdt', 'bookmarkStart', 'bookmarkEnd'
]

# Style element order
STYLE_ORDER = [
    'name', 'aliases', 'basedOn', 'next', 'link', 'autoRedefine',
    'hidden', 'uiPriority', 'semiHidden', 'unhideWhenUsed', 'qFormat',
    'locked', 'personal', 'personalCompose', 'personalReply',
    'rsid', 'pPr', 'rPr', 'tblPr', 'trPr', 'tcPr', 'tblStylePr'
]

# Table element order (for tbl)
TBL_ORDER = [
    'bookmarkStart', 'bookmarkEnd', 'tblPr', 'tblGrid', 'tr'
]

# Body element order - sectPr must be last
# All content elements (p, tbl, sdt, etc.) come first, sectPr comes last
BODY_ORDER = [
    'customXml', 'sdt', 'p', 'tbl', 'bookmarkStart', 'bookmarkEnd',
    'moveFromRangeStart', 'moveFromRangeEnd', 'moveToRangeStart', 'moveToRangeEnd',
    'commentRangeStart', 'commentRangeEnd', 'customXmlInsRangeStart', 'customXmlInsRangeEnd',
    'customXmlDelRangeStart', 'customXmlDelRangeEnd', 'customXmlMoveFromRangeStart',
    'customXmlMoveFromRangeEnd', 'customXmlMoveToRangeStart', 'customXmlMoveToRangeEnd',
    'altChunk', 'sectPr'  # sectPr MUST be last
]


# ============================================================
# Helper functions
# ============================================================

def get_local_name(element):
    """Extract local name from {namespace}tag format"""
    tag = element.tag
    if tag.startswith('{'):
        return tag.split('}')[1]
    return tag


def reorder_children(parent, order_list):
    """
    Reorder children of parent element according to order_list.
    Children not in order_list are placed at the end in original order.
    Returns True if any reordering was done.
    """
    children = list(parent)
    if not children:
        return False

    # Build index map
    order_map = {name: i for i, name in enumerate(order_list)}

    def sort_key(elem):
        local_name = get_local_name(elem)
        if local_name in order_map:
            return (0, order_map[local_name])
        else:
            # Keep original relative order for unknown elements
            return (1, children.index(elem))

    sorted_children = sorted(children, key=sort_key)

    # Check if order changed
    if [id(c) for c in children] == [id(c) for c in sorted_children]:
        return False

    # Remove all children
    for child in children:
        parent.remove(child)

    # Re-add in correct order
    for child in sorted_children:
        parent.append(child)

    return True


def fix_body_order(body_element):
    """
    Fix body element order: sectPr must be last.

    OpenXML requires that sectPr be the last child of body.
    This function moves sectPr to the end while preserving
    the relative order of all other elements.

    Returns True if any fix was made.
    """
    children = list(body_element)
    if not children:
        return False

    # Find sectPr
    sectpr = None
    sectpr_idx = None
    for i, child in enumerate(children):
        if get_local_name(child) == 'sectPr':
            sectpr = child
            sectpr_idx = i
            break

    if sectpr is None:
        return False  # No sectPr to fix

    # Check if sectPr is already last
    if sectpr_idx == len(children) - 1:
        return False  # Already in correct position

    # Move sectPr to the end
    body_element.remove(sectpr)
    body_element.append(sectpr)

    return True


# ============================================================
# Border wrapping fix
# ============================================================

# Border element names that should be inside pBdr, not directly in pPr
BORDER_ELEMENTS = {'top', 'left', 'bottom', 'right', 'between', 'bar'}


def wrap_border_elements(ppr_element):
    """
    Fix misplaced border elements in pPr by wrapping them in pBdr.

    Some code incorrectly puts BottomBorder, TopBorder etc directly in pPr,
    but they should be inside a ParagraphBorders (pBdr) element.

    Args:
        ppr_element: A pPr element to fix

    Returns:
        Number of elements wrapped
    """
    fixes = 0

    # Find misplaced border elements
    misplaced_borders = []
    for child in list(ppr_element):
        local_name = get_local_name(child)
        if local_name in BORDER_ELEMENTS:
            misplaced_borders.append(child)

    if not misplaced_borders:
        return 0

    # Find or create pBdr element
    pbdr = ppr_element.find(w('pBdr'))
    if pbdr is None:
        # Create new pBdr element
        pbdr = ppr_element.makeelement(w('pBdr'), {})

        # Insert pBdr in correct position (after pStyle, before shd)
        inserted = False
        for i, child in enumerate(ppr_element):
            local_name = get_local_name(child)
            # pBdr should come after these elements
            if local_name in ['shd', 'tabs', 'suppressAutoHyphens', 'spacing', 'ind', 'jc']:
                ppr_element.insert(i, pbdr)
                inserted = True
                break
        if not inserted:
            ppr_element.append(pbdr)

    # Move border elements into pBdr
    for border in misplaced_borders:
        ppr_element.remove(border)
        pbdr.append(border)
        fixes += 1

    # Reorder elements inside pBdr
    reorder_children(pbdr, PBDR_ORDER)

    return fixes


# ============================================================
# Main fix function
# ============================================================

def fix_element_order_in_tree(root):
    """
    Fix all known element order issues in an XML tree.

    This enhanced version handles:
    - rPr (RunProperties)
    - pPr (ParagraphProperties)
    - sectPr (SectionProperties)
    - tcPr (TableCellProperties)
    - tblPr (TableProperties)
    - tblBorders, tcBorders
    - lvl (numbering Level)
    - pBdr (ParagraphBorders) [NEW]
    - tcMar (TableCellMargins) [NEW]
    - tblCellMar (TableCellMargins default) [NEW]
    - numbering [NEW]
    - tr (TableRow) [NEW]
    - style [NEW]
    - tbl (Table) [NEW]
    - body (sectPr must be last) [NEW]

    Returns:
        Number of fixes made
    """
    fixes = 0

    # Fix all rPr elements (RunProperties)
    for rpr in root.iter(w('rPr')):
        if reorder_children(rpr, RPR_ORDER):
            fixes += 1

    # Fix all pPr elements (ParagraphProperties)
    for ppr in root.iter(w('pPr')):
        # First wrap any misplaced border elements
        fixes += wrap_border_elements(ppr)
        # Then reorder pPr children
        if reorder_children(ppr, PPR_ORDER):
            fixes += 1

    # Fix all sectPr elements (SectionProperties)
    for sectpr in root.iter(w('sectPr')):
        if reorder_children(sectpr, SECTPR_ORDER):
            fixes += 1

    # Fix all tcPr elements (TableCellProperties)
    for tcpr in root.iter(w('tcPr')):
        if reorder_children(tcpr, TCPR_ORDER):
            fixes += 1

    # Fix all tblPr elements (TableProperties)
    for tblpr in root.iter(w('tblPr')):
        if reorder_children(tblpr, TBLPR_ORDER):
            fixes += 1

    # Fix all tblBorders elements
    for tblborders in root.iter(w('tblBorders')):
        if reorder_children(tblborders, TBLBORDERS_ORDER):
            fixes += 1

    # Fix all tcBorders elements (same order as tblBorders)
    for tcborders in root.iter(w('tcBorders')):
        if reorder_children(tcborders, TBLBORDERS_ORDER):
            fixes += 1

    # Fix all lvl elements (numbering Level)
    for lvl in root.iter(w('lvl')):
        if reorder_children(lvl, LEVEL_ORDER):
            fixes += 1

    # ============================================================
    # NEW fixes
    # ============================================================

    # Fix all pBdr elements (ParagraphBorders)
    for pbdr in root.iter(w('pBdr')):
        if reorder_children(pbdr, PBDR_ORDER):
            fixes += 1

    # Fix all tcMar elements (TableCellMargins)
    for tcmar in root.iter(w('tcMar')):
        if reorder_children(tcmar, TCMAR_ORDER):
            fixes += 1

    # Fix all tblCellMar elements (Table default cell margins)
    for tblcellmar in root.iter(w('tblCellMar')):
        if reorder_children(tblcellmar, TBLCELLMAR_ORDER):
            fixes += 1

    # Fix numbering element order
    for numbering in root.iter(w('numbering')):
        if reorder_children(numbering, NUMBERING_ORDER):
            fixes += 1

    # Fix tr elements (TableRow)
    for tr in root.iter(w('tr')):
        if reorder_children(tr, TR_ORDER):
            fixes += 1

    # Fix style elements
    for style in root.iter(w('style')):
        if reorder_children(style, STYLE_ORDER):
            fixes += 1

    # Fix tbl elements (Table)
    for tbl in root.iter(w('tbl')):
        if reorder_children(tbl, TBL_ORDER):
            fixes += 1

    # Fix body element order (sectPr must be last)
    for body in root.iter(w('body')):
        if fix_body_order(body):
            fixes += 1

    return fixes


def fix_settings(root):
    """Fix settings.xml element order. Returns fix count."""
    fixes = 0

    # Find settings element (root might be the settings element itself)
    settings_elem = root if get_local_name(root) == 'settings' else root.find(w('settings'))

    if settings_elem is not None:
        if reorder_children(settings_elem, SETTINGS_ORDER):
            fixes += 1

    return fixes


# ============================================================
# Table width fix (conservative)
# ============================================================

def fix_table_width_conservative(root):
    """
    Fix table cell width (tcW) to match grid column width (gridCol).

    CONSERVATIVE RULES - only fix when 100% safe:
    1. Only fix type="dxa" or no type attribute (dxa is default)
    2. Skip type="pct" (percentage) - intentional design choice
    3. Skip type="auto" - auto width should not be touched
    4. Only modify existing tcW - never create new elements
    5. Handle gridSpan correctly - sum of spanned columns
    6. Skip if no tblGrid - can't fix without reference
    7. Skip nested tables - too complex, might break layout

    Returns:
        Number of fixes made
    """
    fixes = 0

    # Find all top-level tables (not nested)
    # A nested table is a tbl that has an ancestor tbl
    all_tables = root.findall('.//{%s}tbl' % W_NS)

    for tbl in all_tables:
        # Check if this is a nested table by looking for parent tbl
        # We do this by checking if any ancestor is tbl
        is_nested = False
        parent = tbl
        # Walk up using getparent() if available, or iterate
        # Since ElementTree doesn't have getparent, we check by finding
        # if this tbl is inside another tbl's tc
        for outer_tbl in all_tables:
            if outer_tbl is tbl:
                continue
            # Check if tbl is a descendant of outer_tbl
            for inner in outer_tbl.iter('{%s}tbl' % W_NS):
                if inner is tbl:
                    is_nested = True
                    break
            if is_nested:
                break

        if is_nested:
            continue  # Skip nested tables

        # Get tblGrid
        tbl_grid = tbl.find('{%s}tblGrid' % W_NS)
        if tbl_grid is None:
            continue  # No grid, can't fix

        # Get grid column widths
        grid_cols = tbl_grid.findall('{%s}gridCol' % W_NS)
        if not grid_cols:
            continue  # No columns defined

        grid_widths = []
        valid_grid = True
        for gc in grid_cols:
            w_val = gc.get('{%s}w' % W_NS)
            if w_val is None:
                valid_grid = False
                break
            try:
                grid_widths.append(int(w_val))
            except ValueError:
                valid_grid = False
                break

        if not valid_grid or not grid_widths:
            continue  # Invalid grid widths

        # Process each row
        rows = tbl.findall('{%s}tr' % W_NS)
        for row in rows:
            cells = row.findall('{%s}tc' % W_NS)
            col_idx = 0  # Track which grid column we're at

            for cell in cells:
                if col_idx >= len(grid_widths):
                    break  # More cells than columns, skip rest

                tc_pr = cell.find('{%s}tcPr' % W_NS)
                if tc_pr is None:
                    col_idx += 1
                    continue

                tc_w = tc_pr.find('{%s}tcW' % W_NS)
                if tc_w is None:
                    col_idx += 1
                    continue  # No tcW, don't create one

                # Check type attribute - only fix dxa
                tc_type = tc_w.get('{%s}type' % W_NS)
                if tc_type is not None and tc_type not in ('dxa', ''):
                    # Skip pct, auto, or any other type
                    col_idx += 1
                    continue

                # Check for gridSpan (horizontal merge)
                grid_span = tc_pr.find('{%s}gridSpan' % W_NS)
                span_count = 1
                if grid_span is not None:
                    span_val = grid_span.get('{%s}val' % W_NS)
                    if span_val:
                        try:
                            span_count = int(span_val)
                        except ValueError:
                            span_count = 1

                # Calculate expected width (sum of spanned columns)
                if col_idx + span_count > len(grid_widths):
                    col_idx += span_count
                    continue  # Span exceeds grid, skip

                expected_width = sum(grid_widths[col_idx:col_idx + span_count])

                # Get current tcW value
                current_width = tc_w.get('{%s}w' % W_NS)
                if current_width is None:
                    col_idx += span_count
                    continue

                try:
                    current_width_int = int(current_width)
                except ValueError:
                    col_idx += span_count
                    continue

                # Only fix if there's a significant difference (>5%)
                if expected_width > 0 and abs(current_width_int - expected_width) > expected_width * 0.05:
                    # Fix: set tcW to expected width
                    tc_w.set('{%s}w' % W_NS, str(expected_width))
                    fixes += 1

                col_idx += span_count

    return fixes
