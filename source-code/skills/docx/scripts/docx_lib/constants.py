# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
constants.py - XML namespace definitions for OpenXML documents
"""

from xml.etree import ElementTree as ET

# Core namespaces
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W14_NS = 'http://schemas.microsoft.com/office/word/2010/wordml'
W15_NS = 'http://schemas.microsoft.com/office/word/2012/wordml'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'

# Namespace dict for ElementTree findall
NS = {
    'w': W_NS,
    'w14': W14_NS,
    'w15': W15_NS,
    'r': R_NS,
    'wp': WP_NS,
    'a': A_NS,
}

# Register namespaces to preserve prefixes when writing XML
ET.register_namespace('w', W_NS)
ET.register_namespace('w14', W14_NS)
ET.register_namespace('w15', W15_NS)
ET.register_namespace('r', R_NS)
ET.register_namespace('mc', 'http://schemas.openxmlformats.org/markup-compatibility/2006')
ET.register_namespace('wp', WP_NS)
ET.register_namespace('a', A_NS)
ET.register_namespace('pic', 'http://schemas.openxmlformats.org/drawingml/2006/picture')
ET.register_namespace('m', 'http://schemas.openxmlformats.org/officeDocument/2006/math')
ET.register_namespace('v', 'urn:schemas-microsoft-com:vml')
ET.register_namespace('o', 'urn:schemas-microsoft-com:office:office')
ET.register_namespace('wpc', 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas')
ET.register_namespace('wpg', 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup')
ET.register_namespace('wps', 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape')
ET.register_namespace('w16cid', 'http://schemas.microsoft.com/office/word/2016/wordml/cid')
ET.register_namespace('w16se', 'http://schemas.microsoft.com/office/word/2015/wordml/symex')
ET.register_namespace('cx', 'http://schemas.microsoft.com/office/drawing/2014/chartex')
ET.register_namespace('cx1', 'http://schemas.microsoft.com/office/drawing/2015/9/8/chartex')
ET.register_namespace('aink', 'http://schemas.microsoft.com/office/drawing/2016/ink')
ET.register_namespace('am3d', 'http://schemas.microsoft.com/office/drawing/2017/model3d')


def w(tag):
    """Helper to create {namespace}tag format for wordprocessingml"""
    return f'{{{W_NS}}}{tag}'


def r(tag):
    """Helper to create {namespace}tag format for relationships"""
    return f'{{{R_NS}}}{tag}'
