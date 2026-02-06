#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
Test cases for XML tolerance functions.
These tests verify that malformed XML (like duplicate attributes) can be handled.
"""

import pytest
import tempfile
import os
from xml.etree import ElementTree as ET

# Import the functions we'll implement
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xml_tolerance import fix_duplicate_attributes, safe_parse_xml


class TestFixDuplicateAttributes:
    """Test the fix_duplicate_attributes function."""

    def test_no_duplicates(self):
        """XML without duplicates should remain unchanged."""
        xml = '<root attr1="val1" attr2="val2">content</root>'
        result = fix_duplicate_attributes(xml)
        assert result == xml

    def test_simple_duplicate(self):
        """Simple duplicate attribute should keep first occurrence."""
        xml = '<root attr="val1" attr="val2">content</root>'
        result = fix_duplicate_attributes(xml)
        # Should keep first attr="val1", remove second
        assert 'attr="val1"' in result
        assert result.count('attr=') == 1

    def test_duplicate_with_namespace(self):
        """Duplicate namespaced attribute should be fixed."""
        xml = '<w:comment w:id="1" w:author="Test" w:id="2">content</w:comment>'
        result = fix_duplicate_attributes(xml)
        assert result.count('w:id=') == 1
        assert 'w:id="1"' in result

    def test_multiple_duplicates(self):
        """Multiple different duplicate attributes."""
        xml = '<elem a="1" b="2" a="3" b="4">text</elem>'
        result = fix_duplicate_attributes(xml)
        assert result.count('a=') == 1
        assert result.count('b=') == 1

    def test_complex_docx_comment_xml(self):
        """Real-world style comment XML with duplicates."""
        xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:comment w:id="0" w:author="Test" w:date="2026-01-08T00:00:00Z" w:id="1">
    <w:p><w:r><w:t>Comment text</w:t></w:r></w:p>
  </w:comment>
</w:comments>'''
        result = fix_duplicate_attributes(xml)
        # Should be parseable now
        root = ET.fromstring(result)
        assert root is not None

    def test_preserves_valid_structure(self):
        """Fixing duplicates should preserve overall XML structure."""
        xml = '''<root>
  <child attr="value" attr="dup"/>
  <other name="test"/>
</root>'''
        result = fix_duplicate_attributes(xml)
        root = ET.fromstring(result)
        assert len(root) == 2


class TestSafeParseXml:
    """Test the safe_parse_xml function."""

    def test_valid_xml_file(self):
        """Valid XML file should parse normally."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0"?><root><child/></root>')
            f.flush()
            try:
                tree = safe_parse_xml(f.name)
                assert tree.getroot().tag == 'root'
            finally:
                os.unlink(f.name)

    def test_duplicate_attribute_file(self):
        """File with duplicate attributes should be auto-fixed."""
        xml_content = '<?xml version="1.0"?><root attr="1" attr="2"><child/></root>'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            f.flush()
            try:
                tree = safe_parse_xml(f.name)
                root = tree.getroot()
                assert root.tag == 'root'
                assert root.get('attr') == '1'  # First value kept
            finally:
                os.unlink(f.name)

    def test_comments_xml_with_duplicates(self):
        """Simulate real comments.xml with duplicate w:id."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:comment w:id="0" w:author="Author" w:date="2026-01-08T00:00:00Z" w:initials="A" w:id="0">
    <w:p><w:r><w:t>Test comment</w:t></w:r></w:p>
  </w:comment>
</w:comments>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            f.flush()
            try:
                tree = safe_parse_xml(f.name)
                root = tree.getroot()
                # Should have parsed successfully
                comments = root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment')
                assert len(comments) == 1
            finally:
                os.unlink(f.name)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
