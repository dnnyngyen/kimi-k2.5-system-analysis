# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
xml_tolerance.py - XML parsing with tolerance for malformed XML.

Handles common XML issues in user-uploaded Word documents:
1. Duplicate attributes (regex pre-processing) - XML spec forbids this
2. Mismatched tags, unclosed tags, invalid chars (lxml recover mode)

NOTE: This module now returns lxml objects directly for better namespace handling.
"""

import re
from lxml import etree


def _fix_duplicate_attributes(xml_content: str) -> str:
    """
    Fix duplicate attributes in XML content.

    This MUST be done before parsing because duplicate attributes
    are a fatal error that even lxml recover mode cannot handle.

    Example: <w:comment w:id="0" w:id="1"> -> <w:comment w:id="0">
    """
    tag_pattern = re.compile(r'<([a-zA-Z_:][\w:.-]*)((?:\s+[^>]*?)?)(/?)>', re.DOTALL)
    attr_pattern = re.compile(r'''([a-zA-Z_:][\w:.-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')''')

    def fix_tag(match):
        tag_name = match.group(1)
        attrs_str = match.group(2)
        closing = match.group(3)

        if not attrs_str.strip():
            return match.group(0)

        seen_attrs = {}
        result_attrs = []

        for attr_match in attr_pattern.finditer(attrs_str):
            attr_name = attr_match.group(1)
            attr_value = attr_match.group(2) if attr_match.group(2) is not None else attr_match.group(3)

            if attr_name not in seen_attrs:
                seen_attrs[attr_name] = attr_value
                result_attrs.append(f'{attr_name}="{attr_value}"')

        if result_attrs:
            return f'<{tag_name} {" ".join(result_attrs)}{closing}>'
        else:
            return f'<{tag_name}{closing}>'

    return tag_pattern.sub(fix_tag, xml_content)


def _fix_common_issues(xml_content: str) -> str:
    """Fix issues that must be handled before parsing."""
    # Remove BOM
    if xml_content.startswith('\ufeff'):
        xml_content = xml_content[1:]

    # Fix duplicate attributes (must be done pre-parse)
    xml_content = _fix_duplicate_attributes(xml_content)

    return xml_content


def safe_parse_xml(file_path: str) -> etree._ElementTree:
    """
    Safely parse an XML file with automatic error recovery.

    Handles:
    - Duplicate attributes (pre-processing)
    - Mismatched tags (lxml recover)
    - Unclosed tags (lxml recover)
    - Invalid characters (lxml recover)
    - Not well-formed XML (lxml recover)

    Args:
        file_path: Path to the XML file

    Returns:
        lxml ElementTree object
    """
    # Read and pre-process
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = _fix_common_issues(content)

    parser = etree.XMLParser(
        recover=True,
        remove_blank_text=False,
        strip_cdata=False,
    )

    xml_bytes = content.encode('utf-8')
    lxml_root = etree.fromstring(xml_bytes, parser)
    return etree.ElementTree(lxml_root)


def safe_parse_xml_string(xml_content: str) -> etree._Element:
    """
    Safely parse an XML string with automatic error recovery.

    Args:
        xml_content: XML string

    Returns:
        lxml Element object
    """
    content = _fix_common_issues(xml_content)

    parser = etree.XMLParser(recover=True)
    xml_bytes = content.encode('utf-8')
    return etree.fromstring(xml_bytes, parser)
