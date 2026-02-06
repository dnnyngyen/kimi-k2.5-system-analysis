# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
context.py - DocxContext for managing docx editing sessions.

NOTE: Uses lxml throughout for better namespace handling.
"""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from lxml import etree
from typing import Optional

from ..constants import NS
from .xml_tolerance import safe_parse_xml


class DocxEditError(Exception):
    """Base exception for docx editing errors."""
    pass


class ParagraphNotFoundError(DocxEditError):
    """Raised when paragraph text not found."""
    pass


class AmbiguousTextError(DocxEditError):
    """Raised when text appears multiple times without context."""
    pass


class CommentNotFoundError(DocxEditError):
    """Raised when comment ID not found."""
    pass


class DocxContext:
    """
    Context manager for editing docx files.

    Handles: unzip, parse, save, repack, cleanup.

    Usage:
        with DocxContext("input.docx", "output.docx") as ctx:
            add_comment(ctx, "M-SVI index", "Please define", highlight="M-SVI")
            insert_text(ctx, "The method", after="method", new_text=" and materials")
        # Automatically saves and repacks on exit

    Attributes (for internal use by editing functions):
        work_dir: Path to extracted docx
        doc_tree: Parsed document.xml ElementTree
        body: document.xml body element
    """

    def __init__(self, input_path: str, output_path: str):
        """
        Initialize context.

        Args:
            input_path: Path to input docx file
            output_path: Path for output docx file
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.work_dir: Optional[Path] = None
        self.doc_tree: Optional[etree._ElementTree] = None
        self.body = None
        self._temp_dir = None

    def __enter__(self) -> 'DocxContext':
        """Unzip and parse document."""
        # Validate input file exists
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        # Create temp directory
        self._temp_dir = tempfile.mkdtemp(prefix='docx_edit_')
        self.work_dir = Path(self._temp_dir)

        # Unzip
        with zipfile.ZipFile(self.input_path, 'r') as z:
            z.extractall(self.work_dir)

        # Parse document.xml
        doc_path = self.work_dir / 'word' / 'document.xml'
        self.doc_tree = safe_parse_xml(doc_path)

        self.body = self.doc_tree.getroot().find(f'.//{{{NS["w"]}}}body')

        if self.body is None:
            raise DocxEditError("Invalid docx: document body not found")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Save, repack, and cleanup."""
        if exc_type is None:
            # Save document.xml using lxml serialization
            doc_path = self.work_dir / 'word' / 'document.xml'
            xml_bytes = etree.tostring(
                self.doc_tree.getroot(),
                encoding='utf-8',
                xml_declaration=True
            )
            with open(doc_path, 'wb') as f:
                f.write(xml_bytes)

            # Repack with correct file order (OOXML requirement)
            with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as z:
                all_files = []
                for root, dirs, files in os.walk(self.work_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.work_dir)
                        all_files.append((file_path, arcname))

                # Sort by OOXML required order
                def sort_key(item):
                    arcname = item[1]
                    if arcname == '[Content_Types].xml':
                        return (0, arcname)
                    elif arcname.startswith('_rels'):
                        return (1, arcname)
                    elif arcname.startswith('word/_rels'):
                        return (2, arcname)
                    else:
                        return (3, arcname)

                for file_path, arcname in sorted(all_files, key=sort_key):
                    z.write(file_path, arcname)

        # Cleanup temp directory
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)

        return False  # Don't suppress exceptions

    def find_para(self, text: str):
        """
        Find paragraph containing text.

        Args:
            text: Text to search for (must be unique)

        Returns:
            Paragraph element

        Raises:
            ParagraphNotFoundError: If not found
            AmbiguousTextError: If multiple matches
        """
        matches = [p for p in self.body.findall('.//w:p', NS)
                   if text in ''.join(t.text or '' for t in p.findall('.//w:t', NS))]

        if len(matches) == 0:
            raise ParagraphNotFoundError(f"No paragraph contains '{text}'")
        if len(matches) > 1:
            raise AmbiguousTextError(f"'{text}' matches {len(matches)} paragraphs. Use more specific text.")

        return matches[0]

    def save_xml(self, rel_path: str, tree_or_element):
        """
        Save an XML tree or element to a relative path in work_dir.

        Args:
            rel_path: Relative path (e.g., 'word/comments.xml')
            tree_or_element: lxml ElementTree or Element to save
        """
        full_path = self.work_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle both ElementTree and Element
        if hasattr(tree_or_element, 'getroot'):
            root = tree_or_element.getroot()
        else:
            root = tree_or_element

        xml_bytes = etree.tostring(root, encoding='utf-8', xml_declaration=True)
        with open(full_path, 'wb') as f:
            f.write(xml_bytes)

    def parse_xml(self, rel_path: str) -> Optional[etree._ElementTree]:
        """
        Parse an XML file from work_dir.

        Args:
            rel_path: Relative path

        Returns:
            lxml ElementTree or None if file doesn't exist
        """
        full_path = self.work_dir / rel_path
        if full_path.exists():
            return safe_parse_xml(full_path)
        return None
