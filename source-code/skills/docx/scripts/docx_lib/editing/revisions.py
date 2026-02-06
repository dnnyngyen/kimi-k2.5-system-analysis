"""
revisions.py - Track changes (revision) operations for docx editing.

NOTE: Uses lxml throughout for proper namespace handling.
"""

import os
import copy
import random
from typing import Optional
from lxml import etree
from xml.sax.saxutils import escape as xml_escape

from ..constants import NS
from .context import DocxContext
from .helpers import (
    find_and_split_text,
    get_rpr_from_context,
    new_para_id,
    new_rsid,
    register_rsid,
    utc_now,
    _write_xml,
    W16DU_NS,
)
from .xml_tolerance import safe_parse_xml


def insert_paragraph(
    ctx: DocxContext,
    after_text: str,
    new_text: str,
    author: str = "Kimi"
) -> None:
    """
    Insert new paragraph as tracked insertion.

    Args:
        ctx: DocxContext
        after_text: Unique text in paragraph after which to insert
        new_text: Text content for new paragraph
        author: Revision author

    Example:
        insert_paragraph(ctx, "Chapter 1 conclusion", "This is a new paragraph.")
    """
    after_para = ctx.find_para(after_text)

    timestamp = utc_now()
    para_id = new_para_id()
    text_id = new_para_id()
    rsid = new_rsid()

    # Register rsid in settings.xml
    register_rsid(str(ctx.work_dir), rsid)

    # Auto-retrieve format from context
    rPr = get_rpr_from_context(after_para, str(ctx.work_dir))
    rPr_xml = etree.tostring(rPr, encoding='unicode')

    # Get paragraph properties from source
    pPr = after_para.find(f"{{{NS['w']}}}pPr")
    if pPr is not None:
        pPr_xml = etree.tostring(copy.deepcopy(pPr), encoding='unicode')
    else:
        pPr_xml = f'<w:pPr xmlns:w="{NS["w"]}"><w:ind w:firstLine="420"/></w:pPr>'

    # Escape special XML characters in user-provided content
    safe_author = xml_escape(author)
    safe_text = xml_escape(new_text)

    new_para = etree.fromstring(f'''
    <w:p xmlns:w="{NS['w']}" xmlns:w14="{NS['w14']}" xmlns:w16du="{W16DU_NS}"
         w14:paraId="{para_id}" w14:textId="{text_id}"
         w:rsidR="{rsid}" w:rsidRDefault="{rsid}">
      {pPr_xml}
      <w:ins w:author="{safe_author}" w:date="{timestamp}" w:id="{random.randint(1, 10000)}" w16du:dateUtc="{timestamp}">
        <w:r w:rsidR="{rsid}">{rPr_xml}<w:t>{safe_text}</w:t></w:r>
      </w:ins>
    </w:p>''')

    idx = list(ctx.body).index(after_para)
    ctx.body.insert(idx + 1, new_para)


def insert_text(
    ctx: DocxContext,
    para_text: str,
    after: str,
    new_text: str,
    context: Optional[str] = None,
    author: str = "Kimi"
) -> None:
    """
    Insert text within paragraph as tracked insertion.

    Args:
        ctx: DocxContext
        para_text: Unique text to identify the paragraph
        after: Text after which to insert
        new_text: Text to insert
        context: Disambiguation context if 'after' appears multiple times
        author: Revision author

    Examples:
        # Simple insertion
        insert_text(ctx, "The method was applied", after="method", new_text=" and materials")
        # Result: "The method{++ and materials++} was applied"

        # With disambiguation
        insert_text(ctx, "方法一很好", after="方法", new_text="论", context="使用的方法是")
    """
    para = ctx.find_para(para_text)
    target_run = find_and_split_text(para, after, context)

    pos = list(para).index(target_run) + 1

    timestamp = utc_now()
    rsid = new_rsid()

    # Register rsid in settings.xml
    register_rsid(str(ctx.work_dir), rsid)

    rPr = get_rpr_from_context(para, str(ctx.work_dir), target_run)

    ins_elem = etree.Element(f"{{{NS['w']}}}ins")
    ins_elem.set(f"{{{NS['w']}}}author", author)
    ins_elem.set(f"{{{NS['w']}}}date", timestamp)
    ins_elem.set(f"{{{NS['w']}}}id", str(random.randint(1, 10000)))
    ins_elem.set(f"{{{W16DU_NS}}}dateUtc", timestamp)

    new_run = etree.SubElement(ins_elem, f"{{{NS['w']}}}r")
    new_run.set(f"{{{NS['w']}}}rsidR", rsid)
    new_run.append(copy.deepcopy(rPr))

    t = etree.SubElement(new_run, f"{{{NS['w']}}}t")
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = new_text

    para.insert(pos, ins_elem)


def propose_deletion(
    ctx: DocxContext,
    para_text: str,
    target: Optional[str] = None,
    context: Optional[str] = None,
    author: str = "Kimi"
) -> None:
    """
    Mark text for deletion (tracked deletion).

    Args:
        ctx: DocxContext
        para_text: Unique text to identify the paragraph
        target: Specific text to delete (optional, defaults to entire paragraph)
        context: Disambiguation context if target appears multiple times
        author: Revision author

    Examples:
        # Delete entire paragraph content
        propose_deletion(ctx, "This paragraph should be removed")

        # Delete specific text within paragraph
        propose_deletion(ctx, "The old method was outdated", target="old ")
    """
    para = ctx.find_para(para_text)
    timestamp = utc_now()
    del_id = random.randint(1, 10000)

    if target:
        # Delete specific text
        target_run = find_and_split_text(para, target, context)
        _convert_run_to_deletion(para, target_run, author, timestamp, del_id)
    else:
        # Delete entire paragraph runs
        runs = [child for child in para if child.tag == f"{{{NS['w']}}}r"]

        for run in runs:
            t_elements = run.findall('w:t', NS)
            if not t_elements:
                continue

            _convert_run_to_deletion(para, run, author, timestamp, del_id)
            del_id += 1


def _convert_run_to_deletion(para, run, author, timestamp, del_id):
    """Convert a run to tracked deletion."""
    run_idx = list(para).index(run)

    # Convert <w:t> to <w:delText>
    for t in run.findall('w:t', NS):
        text_content = t.text or ''
        t.tag = f"{{{NS['w']}}}delText"
        if text_content and (text_content[0] == ' ' or text_content[-1] == ' '):
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

    # Remove run from para
    para.remove(run)

    # Create <w:del> wrapper
    del_elem = etree.Element(f"{{{NS['w']}}}del")
    del_elem.set(f"{{{NS['w']}}}id", str(del_id))
    del_elem.set(f"{{{NS['w']}}}author", author)
    del_elem.set(f"{{{NS['w']}}}date", timestamp)
    del_elem.set(f"{{{W16DU_NS}}}dateUtc", timestamp)

    # Put run inside del
    del_elem.append(run)

    # Insert del at original position
    para.insert(run_idx, del_elem)


def reject_insertion(
    ctx: DocxContext,
    para_text: str,
    ins_text: str,
    author: str = "Kimi"
) -> None:
    """
    Reject another author's insertion by wrapping in deletion.

    Args:
        ctx: DocxContext
        para_text: Paragraph containing the insertion
        ins_text: Text inside the <w:ins> to reject
        author: Reviewer name for the rejection
    """
    para = ctx.find_para(para_text)
    timestamp = utc_now()

    # Find <w:ins> containing the text
    for ins_node in para.findall('.//w:ins', NS):
        ins_content = ''.join(t.text or '' for t in ins_node.findall('.//w:t', NS))
        if ins_text in ins_content:
            for run in ins_node.findall('.//w:r', NS):
                for t in run.findall('w:t', NS):
                    t.tag = f"{{{NS['w']}}}delText"

                del_elem = etree.Element(f"{{{NS['w']}}}del")
                del_elem.set(f"{{{NS['w']}}}author", author)
                del_elem.set(f"{{{NS['w']}}}date", timestamp)
                del_elem.set(f"{{{NS['w']}}}id", str(random.randint(1, 10000)))
                del_elem.set(f"{{{W16DU_NS}}}dateUtc", timestamp)

                for child in list(run):
                    del_elem.append(child)
                run.clear()
                run.append(del_elem)
            return


def restore_deletion(
    ctx: DocxContext,
    para_text: str,
    del_text: str,
    author: str = "Kimi"
) -> None:
    """
    Restore another author's deletion by adding insertion after it.

    Args:
        ctx: DocxContext
        para_text: Paragraph containing the deletion
        del_text: Text inside the <w:del> to restore
        author: Reviewer name for the restoration
    """
    para = ctx.find_para(para_text)
    timestamp = utc_now()
    rsid = new_rsid()

    # Find <w:del> containing the text (del is direct child of para)
    for i, child in enumerate(list(para)):
        if child.tag == f"{{{NS['w']}}}del":
            del_content = ''.join(t.text or '' for t in child.findall('.//w:delText', NS))
            if del_text in del_content:
                # Get format from del_node if available
                rPr = child.find('.//w:rPr', NS)
                rPr_copy = copy.deepcopy(rPr) if rPr is not None else None

                # Create insertion element
                ins_elem = etree.Element(f"{{{NS['w']}}}ins")
                ins_elem.set(f"{{{NS['w']}}}author", author)
                ins_elem.set(f"{{{NS['w']}}}date", timestamp)
                ins_elem.set(f"{{{NS['w']}}}id", str(random.randint(1, 10000)))
                ins_elem.set(f"{{{W16DU_NS}}}dateUtc", timestamp)

                ins_r = etree.SubElement(ins_elem, f"{{{NS['w']}}}r")
                ins_r.set(f"{{{NS['w']}}}rsidR", rsid)
                if rPr_copy is not None:
                    ins_r.append(rPr_copy)
                ins_t = etree.SubElement(ins_r, f"{{{NS['w']}}}t")
                ins_t.text = del_text

                # Insert after the <w:del> element
                para.insert(i + 1, ins_elem)

                # Register rsid in settings.xml
                register_rsid(str(ctx.work_dir), rsid)
                return


def enable_track_changes(ctx: DocxContext) -> None:
    """
    Enable track changes in document settings.
    Adds <w:trackRevisions/> to settings.xml.
    """
    settings_path = os.path.join(ctx.work_dir, 'word/settings.xml')
    if not os.path.exists(settings_path):
        return

    tree = safe_parse_xml(settings_path)
    root = tree.getroot()

    if root.find(f'.//{{{NS["w"]}}}trackRevisions') is None:
        track = etree.Element(f"{{{NS['w']}}}trackRevisions")
        root.append(track)
        _write_xml(tree, settings_path)
