# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
docx_lib.editing - High-level API for docx editing operations.

Usage:
    from docx_lib.editing import (
        DocxContext,
        add_comment, reply_comment, resolve_comment, delete_comment,
        insert_paragraph, insert_text, propose_deletion,
        reject_insertion, restore_deletion, enable_track_changes
    )

    with DocxContext("input.docx", "output.docx") as ctx:
        add_comment(ctx, "M-SVI index", "Please define", highlight="M-SVI")
        insert_text(ctx, "The method", after="method", new_text=" and materials")
    # Automatically saves and repacks
"""

from .context import (
    DocxContext,
    DocxEditError,
    ParagraphNotFoundError,
    AmbiguousTextError,
    CommentNotFoundError,
)
from .comments import (
    add_comment,
    reply_comment,
    resolve_comment,
    delete_comment,
)
from .revisions import (
    insert_paragraph,
    insert_text,
    propose_deletion,
    reject_insertion,
    restore_deletion,
    enable_track_changes,
)

__all__ = [
    # Context
    'DocxContext',
    # Exceptions
    'DocxEditError',
    'ParagraphNotFoundError',
    'AmbiguousTextError',
    'CommentNotFoundError',
    # Comments
    'add_comment',
    'reply_comment',
    'resolve_comment',
    'delete_comment',
    # Revisions
    'insert_paragraph',
    'insert_text',
    'propose_deletion',
    'reject_insertion',
    'restore_deletion',
    'enable_track_changes',
]
