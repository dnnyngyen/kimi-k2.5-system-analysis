# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
helpers.py - Internal utilities for editing operations.
Not exported in public API.

NOTE: Uses lxml throughout for proper namespace handling.
"""

import os
import copy
import random
from datetime import datetime, timezone
from lxml import etree

from ..constants import NS, W_NS, W14_NS, W15_NS
from .xml_tolerance import safe_parse_xml

# Additional namespaces for comments
W16CID_NS = 'http://schemas.microsoft.com/office/word/2016/wordml/cid'
W16CEX_NS = 'http://schemas.microsoft.com/office/word/2018/wordml/cex'
W16DU_NS = 'http://schemas.microsoft.com/office/word/2023/wordml/word16du'
MC_NS = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
RELS_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'

# OOXML Standard Namespace Declarations (ISO/IEC 29500, ECMA-376)
# Complete namespace set for Word compatibility
FULL_NSMAP = {
    # Core namespaces
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',

    # Word extension versions
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'w16': 'http://schemas.microsoft.com/office/word/2018/wordml',
    'w16cex': 'http://schemas.microsoft.com/office/word/2018/wordml/cex',
    'w16cid': 'http://schemas.microsoft.com/office/word/2016/wordml/cid',
    'w16du': 'http://schemas.microsoft.com/office/word/2023/wordml/word16du',
    'w16sdtdh': 'http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash',
    'w16sdtfl': 'http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock',
    'w16se': 'http://schemas.microsoft.com/office/word/2015/wordml/symex',

    # Drawing namespaces
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
    'wpc': 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas',
    'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
    'wpi': 'http://schemas.microsoft.com/office/word/2010/wordprocessingInk',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',

    # Office common namespaces
    'o': 'urn:schemas-microsoft-com:office:office',
    'v': 'urn:schemas-microsoft-com:vml',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',

    # Comments reactions (2020+)
    'cr': 'http://schemas.microsoft.com/office/comments/2020/reactions',
}

NS_EXTENDED = {
    **NS,
    'w16cid': W16CID_NS,
    'w16cex': W16CEX_NS,
    'w16du': W16DU_NS,
    'mc': MC_NS,
}

# mc:Ignorable complete list for Word compatibility
MC_IGNORABLE = "w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14"


# ==============================================================================
# ID Generation
# ==============================================================================

def new_para_id():
    """Generate 8-digit uppercase hex for paraId/durableId."""
    return f"{random.randint(1, 0x7FFFFFFE):08X}"


def new_rsid():
    """Generate 8-digit uppercase hex for revision ID."""
    return f"{random.randint(0, 0xFFFFFFFF):08X}"


def utc_now():
    """ISO format UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def register_rsid(work_dir: str, rsid: str) -> None:
    """
    Register rsid in settings.xml.

    Word validates that rsid values used in the document are registered
    in the <w:rsids> list in settings.xml.

    Args:
        work_dir: Working directory containing extracted docx
        rsid: 8-digit hex rsid value to register
    """
    settings_path = os.path.join(work_dir, 'word/settings.xml')
    if not os.path.exists(settings_path):
        return

    tree = safe_parse_xml(settings_path)
    root = tree.getroot()

    # Find or create <w:rsids>
    rsids = root.find(f'.//{{{NS["w"]}}}rsids')
    if rsids is None:
        rsids = etree.SubElement(root, f'{{{NS["w"]}}}rsids')

    # Check if already exists
    for existing in rsids.findall(f'{{{NS["w"]}}}rsid'):
        if existing.get(f'{{{NS["w"]}}}val') == rsid:
            return

    # Add new rsid
    new_rsid_elem = etree.SubElement(rsids, f'{{{NS["w"]}}}rsid')
    new_rsid_elem.set(f'{{{NS["w"]}}}val', rsid)

    _write_xml(tree, settings_path)


# ==============================================================================
# Paragraph Finding
# ==============================================================================

def find_para_by_text(body, text):
    """
    Find paragraph containing text.

    Args:
        body: Document body element
        text: Text to search for

    Returns:
        Paragraph element or None

    Raises:
        ValueError: If multiple paragraphs match
    """
    matches = [p for p in body.findall('.//w:p', NS)
               if text in ''.join(t.text or '' for t in p.findall('.//w:t', NS))]
    if len(matches) > 1:
        raise ValueError(f"'{text}' matches {len(matches)} paragraphs. Use more specific text.")
    return matches[0] if matches else None


# ==============================================================================
# Text Splitting (Character-Level Precision)
# ==============================================================================

def split_runs_for_text(para, search_text, start_index=None):
    """
    Split runs to isolate search_text at character level.

    Args:
        para: Paragraph element
        search_text: Text to isolate
        start_index: Character position to start searching from (for disambiguation)

    Returns:
        The run containing only search_text
    """
    # Only get direct child runs (not nested in ins/del)
    runs = [child for child in para if child.tag == f"{{{NS['w']}}}r"]
    positions = []

    for ri, run in enumerate(runs):
        t = run.find('w:t', NS)
        text = t.text if t is not None and t.text else ''
        for ci, ch in enumerate(text):
            positions.append((ri, ci, ch))

    full_text = ''.join(p[2] for p in positions)

    if start_index is not None:
        idx = full_text.find(search_text, start_index)
    else:
        idx = full_text.find(search_text)

    if idx == -1:
        raise ValueError(f"'{search_text}' not found in paragraph")

    start_pos = idx
    end_pos = idx + len(search_text) - 1

    start_ri, start_ci, _ = positions[start_pos]
    end_ri, end_ci, _ = positions[end_pos]

    first_run = runs[start_ri]
    first_t = first_run.find('w:t', NS)
    first_text = first_t.text
    first_rPr = first_run.find('w:rPr', NS)

    last_run = runs[end_ri]
    last_t = last_run.find('w:t', NS)
    last_text = last_t.text
    last_rPr = last_run.find('w:rPr', NS)

    if start_ri == end_ri:
        prefix = first_text[:start_ci]
        target = search_text
        suffix = first_text[end_ci + 1:]
        rPr_for_target = first_rPr
        rPr_for_suffix = first_rPr
    else:
        prefix = first_text[:start_ci]
        target = search_text
        suffix = last_text[end_ci + 1:]
        rPr_for_target = first_rPr
        rPr_for_suffix = last_rPr

    if start_ri == end_ri and not prefix and not suffix:
        return first_run

    first_run_idx = list(para).index(first_run)
    for ri in range(start_ri, end_ri + 1):
        para.remove(runs[ri])

    def make_run(txt, rPr):
        r = etree.Element(f"{{{NS['w']}}}r")
        if rPr is not None:
            r.append(copy.deepcopy(rPr))
        t = etree.SubElement(r, f"{{{NS['w']}}}t")
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = txt
        return r

    pos = first_run_idx

    if prefix:
        para.insert(pos, make_run(prefix, first_rPr))
        pos += 1

    target_run = make_run(target, rPr_for_target)
    para.insert(pos, target_run)
    pos += 1

    if suffix:
        para.insert(pos, make_run(suffix, rPr_for_suffix))

    return target_run


def find_and_split_text(para, target_text, context=None):
    """
    Find and split target text with character-level precision.

    Args:
        para: Paragraph element
        target_text: Text to locate and isolate
        context: Longer text containing target_text for disambiguation

    Returns:
        Run element containing only target_text

    Raises:
        ValueError: If target_text not unique and no context provided
    """
    # Only get text from direct child runs (not nested in ins/del)
    runs = [child for child in para if child.tag == f"{{{NS['w']}}}r"]
    para_text = ''.join(t.text or '' for r in runs for t in r.findall('w:t', NS))

    if context:
        if para_text.count(context) != 1:
            raise ValueError(f"context '{context}' not unique (found {para_text.count(context)} times)")
        if context.count(target_text) != 1:
            raise ValueError(f"target_text '{target_text}' not unique in context")
        if target_text not in context:
            raise ValueError(f"target_text '{target_text}' not in context")

        context_idx = para_text.find(context)
        target_offset = context.find(target_text)
        start_index = context_idx + target_offset

        return split_runs_for_text(para, target_text, start_index=start_index)
    else:
        if para_text.count(target_text) != 1:
            raise ValueError(f"target_text '{target_text}' not unique (found {para_text.count(target_text)} times), provide context")
        return split_runs_for_text(para, target_text)


# ==============================================================================
# Format Inheritance
# ==============================================================================

def get_rpr_from_context(para, work_dir, insertion_run=None):
    """
    Get rPr from context to ensure inserted content inherits formatting.

    Args:
        para: Target paragraph element
        work_dir: Working directory (for reading styles.xml)
        insertion_run: The run at insertion point (optional)

    Returns:
        Deep copy of rPr element
    """
    if insertion_run is not None:
        rPr = insertion_run.find(f"{{{NS['w']}}}rPr")
        if rPr is not None:
            return copy.deepcopy(rPr)

    for run in para.findall(f".//{{{NS['w']}}}r"):
        rPr = run.find(f"{{{NS['w']}}}rPr")
        if rPr is not None:
            return copy.deepcopy(rPr)

    styles_path = os.path.join(work_dir, 'word/styles.xml')
    if os.path.exists(styles_path):
        styles_tree = safe_parse_xml(styles_path)

        style_id = 'Normal'
        pPr = para.find(f"{{{NS['w']}}}pPr")
        if pPr is not None:
            pStyle = pPr.find(f"{{{NS['w']}}}pStyle")
            if pStyle is not None:
                style_id = pStyle.get(f"{{{NS['w']}}}val")

        visited = set()
        while style_id and style_id not in visited:
            visited.add(style_id)
            for style in styles_tree.findall(f".//{{{NS['w']}}}style"):
                if style.get(f"{{{NS['w']}}}styleId") == style_id:
                    rPr = style.find(f"{{{NS['w']}}}rPr")
                    if rPr is not None:
                        return copy.deepcopy(rPr)
                    basedOn = style.find(f"{{{NS['w']}}}basedOn")
                    style_id = basedOn.get(f"{{{NS['w']}}}val") if basedOn is not None else None
                    break
            else:
                break

    return etree.Element(f"{{{NS['w']}}}rPr")


# ==============================================================================
# Comment Paragraph Building
# ==============================================================================

def build_comment_paragraph(text, para_id, rPr_xml='', rsid=None):
    """
    Build comment paragraph element with line break support.
    Converts \\n in text to <w:br/> elements.

    Structure follows OOXML spec: first run must contain annotationRef.

    Args:
        text: Comment text content
        para_id: Paragraph ID
        rPr_xml: Optional run properties XML string
        rsid: Optional revision save ID (will be generated if not provided)

    Returns:
        tuple: (paragraph element, rsid used)
    """
    if rsid is None:
        rsid = new_rsid()

    p = etree.Element(f"{{{NS['w']}}}p")
    p.set(f"{{{NS['w14']}}}paraId", para_id)
    p.set(f"{{{NS['w14']}}}textId", new_para_id())
    # Add rsid attributes for Word compatibility
    p.set(f"{{{NS['w']}}}rsidR", rsid)
    p.set(f"{{{NS['w']}}}rsidRDefault", rsid)
    p.set(f"{{{NS['w']}}}rsidP", rsid)

    # First run: annotationRef (required by OOXML spec)
    anno_run = etree.SubElement(p, f"{{{NS['w']}}}r")
    anno_run.set(f"{{{NS['w']}}}rsidR", rsid)
    anno_rPr = etree.SubElement(anno_run, f"{{{NS['w']}}}rPr")
    anno_rStyle = etree.SubElement(anno_rPr, f"{{{NS['w']}}}rStyle")
    anno_rStyle.set(f"{{{NS['w']}}}val", "CommentReference")
    etree.SubElement(anno_run, f"{{{NS['w']}}}annotationRef")

    # Text content runs
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line:
            r = etree.SubElement(p, f"{{{NS['w']}}}r")
            r.set(f"{{{NS['w']}}}rsidR", rsid)
            if rPr_xml:
                r.append(etree.fromstring(rPr_xml))
            t = etree.SubElement(r, f"{{{NS['w']}}}t")
            t.text = line
        if i < len(lines) - 1:
            br_r = etree.SubElement(p, f"{{{NS['w']}}}r")
            br_r.set(f"{{{NS['w']}}}rsidR", rsid)
            etree.SubElement(br_r, f"{{{NS['w']}}}br")

    return p, rsid


# ==============================================================================
# File Helpers
# ==============================================================================

def _write_xml(element_or_tree, path):
    """Write XML with proper declaration using lxml."""
    if hasattr(element_or_tree, 'getroot'):
        root = element_or_tree.getroot()
    else:
        root = element_or_tree
    xml_bytes = etree.tostring(root, encoding='utf-8', xml_declaration=True)
    with open(path, 'wb') as f:
        f.write(xml_bytes)


def _create_comments_xml_root():
    """Create comments.xml root with full namespace declarations using lxml nsmap."""
    root = etree.Element(f"{{{FULL_NSMAP['w']}}}comments", nsmap=FULL_NSMAP)
    root.set(f"{{{FULL_NSMAP['mc']}}}Ignorable", MC_IGNORABLE)
    return root


def _create_comments_extended_root():
    """Create commentsExtended.xml root with full namespace declarations."""
    root = etree.Element(f"{{{FULL_NSMAP['w15']}}}commentsEx", nsmap=FULL_NSMAP)
    root.set(f"{{{FULL_NSMAP['mc']}}}Ignorable", MC_IGNORABLE)
    return root


def _create_comments_ids_root():
    """Create commentsIds.xml root with full namespace declarations."""
    root = etree.Element(f"{{{FULL_NSMAP['w16cid']}}}commentsIds", nsmap=FULL_NSMAP)
    root.set(f"{{{FULL_NSMAP['mc']}}}Ignorable", MC_IGNORABLE)
    return root


def _create_comments_extensible_root():
    """Create commentsExtensible.xml root with full namespace declarations."""
    root = etree.Element(f"{{{FULL_NSMAP['w16cex']}}}commentsExtensible", nsmap=FULL_NSMAP)
    root.set(f"{{{FULL_NSMAP['mc']}}}Ignorable", MC_IGNORABLE)
    return root


def _create_people_root():
    """Create people.xml root with full namespace declarations."""
    root = etree.Element(f"{{{FULL_NSMAP['w15']}}}people", nsmap=FULL_NSMAP)
    root.set(f"{{{FULL_NSMAP['mc']}}}Ignorable", MC_IGNORABLE)
    return root


def ensure_comments_file(work_dir, rel_path, root_tag, namespace):
    """Create comments file if not exists with proper namespace declarations."""
    full_path = os.path.join(work_dir, rel_path)
    if not os.path.exists(full_path):
        # Use specialized root creators for proper namespace handling
        if 'comments.xml' == os.path.basename(rel_path):
            root = _create_comments_xml_root()
        elif 'commentsExtended.xml' == os.path.basename(rel_path):
            root = _create_comments_extended_root()
        elif 'commentsIds.xml' == os.path.basename(rel_path):
            root = _create_comments_ids_root()
        elif 'commentsExtensible.xml' == os.path.basename(rel_path):
            root = _create_comments_extensible_root()
        elif 'people.xml' == os.path.basename(rel_path):
            root = _create_people_root()
        else:
            # Fallback for unknown files
            root = etree.Element(f"{{{namespace}}}{root_tag}")

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        _write_xml(root, full_path)


def ensure_comment_relationships(work_dir):
    """Add comment relationships to document.xml.rels."""
    rels_path = os.path.join(work_dir, 'word/_rels/document.xml.rels')
    tree = safe_parse_xml(rels_path)
    root = tree.getroot()

    existing_targets = set()
    existing_ids = []
    for rel in root.findall(f'.//{{{RELS_NS}}}Relationship'):
        target = rel.get('Target')
        if target:
            existing_targets.add(target)
        rid = rel.get('Id', 'rId0')
        if rid.startswith('rId'):
            try:
                existing_ids.append(int(rid[3:]))
            except ValueError:
                pass

    comment_rels = [
        ('comments.xml', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments'),
        ('commentsExtended.xml', 'http://schemas.microsoft.com/office/2011/relationships/commentsExtended'),
        ('commentsIds.xml', 'http://schemas.microsoft.com/office/2016/09/relationships/commentsIds'),
        ('commentsExtensible.xml', 'http://schemas.microsoft.com/office/2018/08/relationships/commentsExtensible'),
        ('people.xml', 'http://schemas.microsoft.com/office/2011/relationships/people'),
    ]

    next_id = max(existing_ids, default=0) + 1

    for target, rel_type in comment_rels:
        if target not in existing_targets:
            rel = etree.SubElement(root, f'{{{RELS_NS}}}Relationship')
            rel.set('Id', f'rId{next_id}')
            rel.set('Type', rel_type)
            rel.set('Target', target)
            next_id += 1

    _write_xml(tree, rels_path)


def ensure_comment_content_types(work_dir):
    """Add comment content types to [Content_Types].xml."""
    ct_path = os.path.join(work_dir, '[Content_Types].xml')
    tree = safe_parse_xml(ct_path)
    root = tree.getroot()

    existing_parts = set()
    for override in root.findall(f'.//{{{CT_NS}}}Override'):
        part_name = override.get('PartName')
        if part_name:
            existing_parts.add(part_name)

    overrides = [
        ('/word/comments.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml'),
        ('/word/commentsExtended.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml'),
        ('/word/commentsIds.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.commentsIds+xml'),
        ('/word/commentsExtensible.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtensible+xml'),
        ('/word/people.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.people+xml'),
    ]

    for part_name, content_type in overrides:
        if part_name not in existing_parts:
            override = etree.SubElement(root, f'{{{CT_NS}}}Override')
            override.set('PartName', part_name)
            override.set('ContentType', content_type)

    _write_xml(tree, ct_path)


# ==============================================================================
# Comment File Updates
# ==============================================================================

def get_next_comment_id(work_dir):
    """Get the next available comment ID."""
    comments_path = os.path.join(work_dir, 'word/comments.xml')
    if os.path.exists(comments_path):
        tree = safe_parse_xml(comments_path)
        existing_ids = [int(c.get(f"{{{NS['w']}}}id", 0))
                       for c in tree.getroot().findall('.//w:comment', NS)]
        return str(max(existing_ids, default=-1) + 1)
    return "0"


def update_comment_files(work_dir, comment_id, comment_text, author, initials,
                         timestamp, para_id, durable_id, parent_para_id=None):
    """
    Update the 5 comment-related XML files.

    Args:
        work_dir: Working directory
        comment_id: Comment ID (string)
        comment_text: Comment content
        author: Author name
        initials: Author initials
        timestamp: ISO UTC timestamp
        para_id: Paragraph ID
        durable_id: Durable ID
        parent_para_id: Parent's paraId (for replies)
    """
    # 1. comments.xml
    comments_path = os.path.join(work_dir, 'word/comments.xml')
    ensure_comments_file(work_dir, 'word/comments.xml', 'comments', NS['w'])
    comments_tree = safe_parse_xml(comments_path)
    comments_root = comments_tree.getroot()

    comment = etree.Element(f"{{{NS['w']}}}comment")
    comment.set(f"{{{NS['w']}}}id", comment_id)
    comment.set(f"{{{NS['w']}}}author", author)
    comment.set(f"{{{NS['w']}}}initials", initials)
    comment.set(f"{{{NS['w']}}}date", timestamp)

    comment_para, rsid = build_comment_paragraph(comment_text, para_id)
    comment.append(comment_para)
    comments_root.append(comment)
    _write_xml(comments_tree, comments_path)

    # Register rsid in settings.xml
    register_rsid(work_dir, rsid)

    # 2. commentsExtended.xml
    ext_path = os.path.join(work_dir, 'word/commentsExtended.xml')
    ensure_comments_file(work_dir, 'word/commentsExtended.xml', 'commentsEx', NS['w15'])
    ext_tree = safe_parse_xml(ext_path)
    ext_root = ext_tree.getroot()

    comment_ex = etree.Element(f"{{{NS['w15']}}}commentEx")
    comment_ex.set(f"{{{NS['w15']}}}paraId", para_id)
    if parent_para_id:
        comment_ex.set(f"{{{NS['w15']}}}paraIdParent", parent_para_id)
    comment_ex.set(f"{{{NS['w15']}}}done", "0")
    ext_root.append(comment_ex)
    _write_xml(ext_tree, ext_path)

    # 3. commentsIds.xml
    ids_path = os.path.join(work_dir, 'word/commentsIds.xml')
    ensure_comments_file(work_dir, 'word/commentsIds.xml', 'commentsIds', W16CID_NS)
    ids_tree = safe_parse_xml(ids_path)
    ids_root = ids_tree.getroot()

    comment_id_elem = etree.Element(f"{{{W16CID_NS}}}commentId")
    comment_id_elem.set(f"{{{W16CID_NS}}}paraId", para_id)
    comment_id_elem.set(f"{{{W16CID_NS}}}durableId", durable_id)
    ids_root.append(comment_id_elem)
    _write_xml(ids_tree, ids_path)

    # 4. commentsExtensible.xml
    extensible_path = os.path.join(work_dir, 'word/commentsExtensible.xml')
    ensure_comments_file(work_dir, 'word/commentsExtensible.xml', 'commentsExtensible', W16CEX_NS)
    extensible_tree = safe_parse_xml(extensible_path)
    extensible_root = extensible_tree.getroot()

    extensible_elem = etree.Element(f"{{{W16CEX_NS}}}commentExtensible")
    extensible_elem.set(f"{{{W16CEX_NS}}}durableId", durable_id)
    extensible_elem.set(f"{{{W16CEX_NS}}}dateUtc", timestamp)
    extensible_root.append(extensible_elem)
    _write_xml(extensible_tree, extensible_path)

    # 5. people.xml - store author information
    people_path = os.path.join(work_dir, 'word/people.xml')
    ensure_comments_file(work_dir, 'word/people.xml', 'people', NS['w15'])
    people_tree = safe_parse_xml(people_path)
    people_root = people_tree.getroot()

    # Check if author already exists
    existing_authors = set()
    for person in people_root.findall(f'.//{{{NS["w15"]}}}person'):
        existing_authors.add(person.get(f'{{{NS["w15"]}}}author'))

    if author not in existing_authors:
        person = etree.Element(f"{{{NS['w15']}}}person")
        person.set(f"{{{NS['w15']}}}author", author)
        # Add presenter element with userId (using author name as placeholder)
        presenter = etree.SubElement(person, f"{{{NS['w15']}}}presenceInfo")
        presenter.set(f"{{{NS['w15']}}}providerId", "None")
        presenter.set(f"{{{NS['w15']}}}userId", author)
        people_root.append(person)
        _write_xml(people_tree, people_path)


def insert_comment_anchor(para, comment_id, first_run, last_run):
    """Insert comment anchor elements into paragraph."""
    range_start = etree.Element(f"{{{NS['w']}}}commentRangeStart")
    range_start.set(f"{{{NS['w']}}}id", comment_id)
    idx = list(para).index(first_run)
    para.insert(idx, range_start)

    range_end = etree.Element(f"{{{NS['w']}}}commentRangeEnd")
    range_end.set(f"{{{NS['w']}}}id", comment_id)

    ref_run = etree.fromstring(f'''
    <w:r xmlns:w="{NS['w']}">
        <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
        <w:commentReference w:id="{comment_id}"/>
    </w:r>''')

    idx = list(para).index(last_run)
    para.insert(idx + 1, range_end)
    para.insert(idx + 2, ref_run)


def get_parent_para_id(work_dir, parent_comment_id):
    """Get the paraId of a parent comment."""
    comments_path = os.path.join(work_dir, 'word/comments.xml')
    if not os.path.exists(comments_path):
        return None

    comments_tree = safe_parse_xml(comments_path)
    for c in comments_tree.getroot().findall('.//w:comment', NS):
        if c.get(f"{{{NS['w']}}}id") == str(parent_comment_id):
            p = c.find('.//w:p', NS)
            if p is not None:
                return p.get(f"{{{NS['w14']}}}paraId")
    return None


def insert_reply_anchor(doc_tree, parent_comment_id, reply_id):
    """Insert reply's anchor elements next to parent's anchor."""
    doc_root = doc_tree.getroot()

    parent_range_start = doc_root.find(f'.//w:commentRangeStart[@w:id="{parent_comment_id}"]', NS)
    if parent_range_start is not None:
        for p in doc_root.iter():
            if parent_range_start in list(p):
                idx = list(p).index(parent_range_start)
                reply_range_start = etree.Element(f"{{{NS['w']}}}commentRangeStart")
                reply_range_start.set(f"{{{NS['w']}}}id", reply_id)
                p.insert(idx + 1, reply_range_start)
                break

    parent_range_end = doc_root.find(f'.//w:commentRangeEnd[@w:id="{parent_comment_id}"]', NS)
    if parent_range_end is not None:
        for p in doc_root.iter():
            if parent_range_end in list(p):
                idx = list(p).index(parent_range_end)

                ref_idx = idx + 1
                while ref_idx < len(list(p)):
                    elem = list(p)[ref_idx]
                    if elem.find('.//w:commentReference', NS) is not None:
                        break
                    ref_idx += 1

                reply_range_end = etree.Element(f"{{{NS['w']}}}commentRangeEnd")
                reply_range_end.set(f"{{{NS['w']}}}id", reply_id)

                reply_ref_run = etree.fromstring(f'''
                <w:r xmlns:w="{NS['w']}">
                    <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
                    <w:commentReference w:id="{reply_id}"/>
                </w:r>''')

                p.insert(ref_idx + 1, reply_range_end)
                p.insert(ref_idx + 2, reply_ref_run)
                break
