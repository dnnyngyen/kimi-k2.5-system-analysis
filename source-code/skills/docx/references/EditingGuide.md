<!-- NOTICE: This file was extracted from the Kimi K2.5 agent environment.
     Provided in response to plain-English questions. Maintainer does not claim
     copyright. Included for research under CC0 1.0. See LICENSE for details. -->

# Editing Guide

Complete reference for `docx_lib.editing`. Read this to complete any comment/revision task.

---

## 1. Quick Reference

### 1.1 Functions

| Function | Purpose |
|----------|---------|
| `add_comment` | Add comment to paragraph with optional highlight |
| `reply_comment` | Reply to existing comment (threaded) |
| `resolve_comment` | Mark comment as resolved |
| `delete_comment` | Delete comment and all its replies |
| `insert_text` | Insert text at specific position (tracked) |
| `insert_paragraph` | Insert new paragraph after target (tracked) |
| `propose_deletion` | Mark text/paragraph for deletion (tracked) |
| `reject_insertion` | Reject another author's insertion |
| `restore_deletion` | Restore another author's deletion |
| `enable_track_changes` | Enable revision tracking in document |

### 1.2 Parameter Semantics

| Parameter | Meaning | Example |
|-----------|---------|---------|
| `para_text` | Text to locate the paragraph (partial OK, must be unique in document) | `"M-SVI index was"` |
| `comment` | Comment content (supports \\n for line breaks) | `"Please define M-SVI"` |
| `highlight` | Text to highlight for comment (optional, omit to highlight entire paragraph) | `"M-SVI"` |
| `after` | Insert new text after this string | `"method"` |
| `target` | Text to delete (if None, delete entire paragraph) | `"redundant phrase"` |
| `context` | Longer text containing target for disambiguation | `"使用的方法是"` |
| `comment_id` | ID returned by add_comment (string) | `"0"` |

### 1.3 Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `ParagraphNotFoundError` | `para_text` not found in document | Use more/less specific text |
| `AmbiguousTextError` | Multiple paragraphs match `para_text` | Use more specific text or `context` |
| `CommentNotFoundError` | `comment_id` doesn't exist | Check ID from add_comment return |
| `ValueError` | `highlight`/`target` not found in paragraph | Verify text exists exactly |

### 1.4 Examples

```python
from scripts.docx_lib.editing import *

with DocxContext("input.docx", "output.docx") as ctx:
    # Highlight a term
    cid = add_comment(ctx, "The API uses OAuth2 for authentication",
                      "Add a code example.",
                      highlight="OAuth2")

    # Highlight a long sentence
    add_comment(ctx, "The new caching layer reduces database queries by maintaining frequently accessed data in memory, which significantly improves response times for read-heavy workloads",
                "This claim needs benchmark data.",
                highlight="The new caching layer reduces database queries by maintaining frequently accessed data in memory, which significantly improves response times for read-heavy workloads")

    # Highlight entire paragraph (omit highlight parameter)
    add_comment(ctx, "This section describes the installation process",
                "Split into subsections.")

    # Reply to comment
    reply_comment(ctx, cid, "Will add example.")

    # Insert text
    insert_text(ctx, "Supports JSON format",
                after="JSON", new_text=" and XML")

    # Propose deletion
    propose_deletion(ctx, "This legacy feature will be removed",
                     target="legacy feature will be removed")
```

### 1.5 Verification (Mandatory)

After editing, always verify:

```bash
pandoc output.docx -t markdown --track-changes=all
```

Check for:
- `{++inserted text++}` — insertions
- `{--deleted text--}` — deletions
- `[text]{.comment-start id="0" author="Kimi"}` — comments

**If count mismatches expected edits, changes were not saved. Do not deliver.**

---

## 2. Usage Patterns

### 2.1 Text Anchoring

This API uses **text as anchors** to locate positions. `insert_text` and `propose_deletion` modify paragraph text, which may invalidate anchors for subsequent operations. Plan operation order based on dependencies.

### 2.2 Highlight Selection

Highlight **what the comment is about**, not just where to anchor it. Flexibly choose word, phrase, clause, or sentence to ensure professionalism, accuracy, and readability.

When `highlight` is omitted, the entire paragraph is highlighted.

### 2.3 Disambiguation

When `highlight`, `after`, or `target` appears multiple times, use `context`:

```python
# Paragraph: "方法一很好。使用的方法是正确的。"
# Want second "方法"

add_comment(ctx, "使用的方法是正确的",
            "Which method?",
            highlight="方法",
            context="使用的方法是")  # Finds within this context
```

**Rules**:
- `context` must be unique in the paragraph
- Target text must be unique within `context`

### 2.4 Handling Others' Revisions

**Golden rule**: Never modify text inside another author's `<w:ins>` or `<w:del>`. Use nesting.

| Scenario | Function | Effect |
|----------|----------|--------|
| Reject their insertion | `reject_insertion(ctx, para_text, ins_text)` | Wraps their insertion in your deletion |
| Restore their deletion | `restore_deletion(ctx, para_text, del_text)` | Adds your insertion after their deletion |

### 2.5 Quality Standards

- **Minimal diff**: Change only what's necessary
- **Pair deletion with comment**: Always explain why content is removed
- **Match document language**: Chinese doc → Chinese comments

---

## 3. Troubleshooting

### 3.1 Common Errors

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ParagraphNotFoundError` | Text doesn't exist or has extra spaces | Copy exact text from document |
| `AmbiguousTextError` | Text appears in multiple paragraphs | Use longer, more unique text |
| Comment not visible in Word | Verification not run | Run pandoc check before delivery |
| Reply not threaded | Wrong `comment_id` | Use ID returned by `add_comment` |

### 3.2 Verification Failed

If pandoc output doesn't show expected markers:

1. **Missing comments**: Check `add_comment` didn't raise error
2. **Missing revisions**: Ensure `enable_track_changes(ctx)` was called
3. **Wrong count**: Some edits failed silently — check each operation's target text exists
