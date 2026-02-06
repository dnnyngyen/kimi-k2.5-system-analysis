# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
comments.py - Comment operations for docx editing.

NOTE: Uses lxml throughout for proper namespace handling.
"""

import os
from typing import List, Optional

from ..constants import NS, W14_NS, W15_NS
from .context import DocxContext, CommentNotFoundError
from .helpers import (
    find_and_split_text,
    new_para_id,
    utc_now,
    get_next_comment_id,
    update_comment_files,
    insert_comment_anchor,
    get_parent_para_id,
    insert_reply_anchor,
    ensure_comment_relationships,
    ensure_comment_content_types,
    _write_xml,
)
from .xml_tolerance import safe_parse_xml


def add_comment(
    ctx: DocxContext,
    para_text: str,
    comment: str,
    highlight: Optional[str] = None,
    context: Optional[str] = None,
    author: str = "Kimi",
    initials: str = "K"
) -> str:
    """
    Add comment to paragraph.

    Args:
        ctx: DocxContext from context manager
        para_text: Unique text to identify the paragraph
        comment: Comment content (supports \\n for line breaks)
        highlight: Text to highlight (optional, defaults to entire paragraph)
        context: Longer text for disambiguation when highlight appears multiple times
        author: Comment author name
        initials: Author initials

    Returns:
        Comment ID (string)

    Examples:
        # Comment on unique text
        add_comment(ctx, "M-SVI index was", "Please define M-SVI", highlight="M-SVI")

        # Disambiguation when highlight appears multiple times
        # Paragraph: "方法一很好。使用的方法是正确的。"
        add_comment(ctx, "使用的方法是", "Which method?",
                    highlight="方法", context="使用的方法是")
    """
    para = ctx.find_para(para_text)

    if highlight:
        target_run = find_and_split_text(para, highlight, context)
        first_run = last_run = target_run
    else:
        # Get direct child runs only (not nested in ins/del)
        all_runs = [child for child in para if child.tag == f"{{{NS['w']}}}r"]
        if not all_runs:
            raise ValueError(f"Paragraph '{para_text}' has no text runs to comment on")
        first_run = all_runs[0]
        last_run = all_runs[-1]

    timestamp = utc_now()
    para_id = new_para_id()
    durable_id = new_para_id()
    comment_id = get_next_comment_id(str(ctx.work_dir))

    # Add anchor to document.xml
    insert_comment_anchor(para, comment_id, first_run, last_run)

    # Update the 4 comment files
    update_comment_files(str(ctx.work_dir), comment_id, comment, author, initials,
                         timestamp, para_id, durable_id)

    # Update relationships and content types
    ensure_comment_relationships(str(ctx.work_dir))
    ensure_comment_content_types(str(ctx.work_dir))

    return comment_id


def reply_comment(
    ctx: DocxContext,
    comment_id: str,
    reply: str,
    author: str = "Kimi",
    initials: str = "K"
) -> str:
    """
    Reply to an existing comment.

    Args:
        ctx: DocxContext
        comment_id: ID of parent comment to reply to
        reply: Reply text
        author: Reply author name
        initials: Author initials

    Returns:
        Reply comment ID
    """
    timestamp = utc_now()
    reply_para_id = new_para_id()
    reply_durable_id = new_para_id()

    # Find parent comment's paraId
    parent_para_id = get_parent_para_id(str(ctx.work_dir), comment_id)
    if parent_para_id is None:
        raise CommentNotFoundError(f"Parent comment {comment_id} not found")

    # Get next comment ID
    reply_id = get_next_comment_id(str(ctx.work_dir))

    # Add reply's own anchor in document.xml
    insert_reply_anchor(ctx.doc_tree, comment_id, reply_id)

    # Update the 4 comment files
    update_comment_files(str(ctx.work_dir), reply_id, reply, author, initials,
                         timestamp, reply_para_id, reply_durable_id,
                         parent_para_id=parent_para_id)

    return reply_id


def resolve_comment(ctx: DocxContext, comment_id: str) -> None:
    """
    Mark comment as resolved (done=1).

    Args:
        ctx: DocxContext
        comment_id: Comment ID to resolve
    """
    # Find comment's paraId first
    para_id = get_parent_para_id(str(ctx.work_dir), comment_id)
    if para_id is None:
        raise CommentNotFoundError(f"Comment {comment_id} not found")

    ext_path = os.path.join(ctx.work_dir, 'word/commentsExtended.xml')
    if not os.path.exists(ext_path):
        return

    tree = safe_parse_xml(ext_path)
    for ex in tree.getroot().findall(f'.//{{{NS["w15"]}}}commentEx'):
        if ex.get(f"{{{NS['w15']}}}paraId") == para_id:
            ex.set(f"{{{NS['w15']}}}done", "1")

    _write_xml(tree, ext_path)


def delete_comment(ctx: DocxContext, comment_id: str) -> List[str]:
    """
    Delete comment and all its replies.

    Args:
        ctx: DocxContext
        comment_id: Comment ID to delete

    Returns:
        List of deleted comment IDs (includes replies)
    """
    deleted_ids = []
    work_dir = str(ctx.work_dir)

    # Find the comment's paraId
    comments_path = os.path.join(work_dir, 'word/comments.xml')
    if not os.path.exists(comments_path):
        return deleted_ids

    comments_tree = safe_parse_xml(comments_path)
    comments_root = comments_tree.getroot()

    target_para_id = None
    for c in comments_root.findall('.//w:comment', NS):
        if c.get(f"{{{NS['w']}}}id") == str(comment_id):
            p = c.find('.//w:p', NS)
            if p is not None:
                target_para_id = p.get(f"{{{NS['w14']}}}paraId")
            break

    if target_para_id is None:
        return deleted_ids

    # Find all replies
    ext_path = os.path.join(work_dir, 'word/commentsExtended.xml')
    reply_para_ids = set()
    if os.path.exists(ext_path):
        ext_tree = safe_parse_xml(ext_path)
        for ex in ext_tree.getroot().findall(f'.//{{{NS["w15"]}}}commentEx'):
            if ex.get(f"{{{NS['w15']}}}paraIdParent") == target_para_id:
                reply_para_ids.add(ex.get(f"{{{NS['w15']}}}paraId"))

    # Map paraId to comment_id for replies
    reply_comment_ids = []
    for c in comments_root.findall('.//w:comment', NS):
        p = c.find('.//w:p', NS)
        if p is not None and p.get(f"{{{NS['w14']}}}paraId") in reply_para_ids:
            reply_comment_ids.append(c.get(f"{{{NS['w']}}}id"))

    # Delete all
    all_ids_to_delete = [str(comment_id)] + reply_comment_ids

    for cid in all_ids_to_delete:
        _delete_single_comment(ctx, cid)
        deleted_ids.append(cid)

    return deleted_ids


def _delete_single_comment(ctx: DocxContext, comment_id: str):
    """Delete a single comment from all 5 files."""
    doc_root = ctx.doc_tree.getroot()
    work_dir = str(ctx.work_dir)

    # 1. Remove anchors from document.xml
    for elem in list(doc_root.iter()):
        for child in list(elem):
            if child.tag == f"{{{NS['w']}}}commentRangeStart":
                if child.get(f"{{{NS['w']}}}id") == str(comment_id):
                    elem.remove(child)
            elif child.tag == f"{{{NS['w']}}}commentRangeEnd":
                if child.get(f"{{{NS['w']}}}id") == str(comment_id):
                    elem.remove(child)
            elif child.tag == f"{{{NS['w']}}}r":
                ref = child.find('.//w:commentReference', NS)
                if ref is not None and ref.get(f"{{{NS['w']}}}id") == str(comment_id):
                    elem.remove(child)

    # 2. Get paraId before removing from comments.xml (needed for other files)
    para_id = None
    comments_path = os.path.join(work_dir, 'word/comments.xml')
    if os.path.exists(comments_path):
        tree = safe_parse_xml(comments_path)
        root = tree.getroot()
        for c in list(root.findall('.//w:comment', NS)):
            if c.get(f"{{{NS['w']}}}id") == str(comment_id):
                p = c.find('.//w:p', NS)
                if p is not None:
                    para_id = p.get(f"{{{NS['w14']}}}paraId")
                root.remove(c)
        _write_xml(tree, comments_path)

    if para_id is None:
        return

    # 3. Remove from commentsExtended.xml
    ext_path = os.path.join(work_dir, 'word/commentsExtended.xml')
    if os.path.exists(ext_path):
        tree = safe_parse_xml(ext_path)
        root = tree.getroot()
        for ex in list(root):
            if ex.get(f"{{{NS['w15']}}}paraId") == para_id:
                root.remove(ex)
        _write_xml(tree, ext_path)

    # 4. Remove from commentsIds.xml and get durableId for step 5
    W16CID_NS = 'http://schemas.microsoft.com/office/word/2016/wordml/cid'
    durable_id = None
    ids_path = os.path.join(work_dir, 'word/commentsIds.xml')
    if os.path.exists(ids_path):
        tree = safe_parse_xml(ids_path)
        root = tree.getroot()
        for cid in list(root):
            if cid.get(f"{{{W16CID_NS}}}paraId") == para_id:
                durable_id = cid.get(f"{{{W16CID_NS}}}durableId")
                root.remove(cid)
        _write_xml(tree, ids_path)

    # 5. Remove from commentsExtensible.xml using durableId
    W16CEX_NS = 'http://schemas.microsoft.com/office/word/2018/wordml/cex'
    extensible_path = os.path.join(work_dir, 'word/commentsExtensible.xml')
    if os.path.exists(extensible_path) and durable_id:
        tree = safe_parse_xml(extensible_path)
        root = tree.getroot()
        for ext in list(root):
            if ext.get(f"{{{W16CEX_NS}}}durableId") == durable_id:
                root.remove(ext)
        _write_xml(tree, extensible_path)
