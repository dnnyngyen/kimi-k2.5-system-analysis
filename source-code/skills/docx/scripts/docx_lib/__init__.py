# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""
docx_lib - Shared library for docx validation, fixing, and editing

Modules:
    constants: XML namespace definitions
    element_order: OpenXML element order definitions and fix functions
    business_rules: Business rule validation (table grid, image aspect, comments)
    editing: High-level API for comments and track changes
"""

from .constants import W_NS, W14_NS, W15_NS, R_NS, WP_NS, A_NS, NS, w, r
from .element_order import (
    RPR_ORDER, PPR_ORDER, SECTPR_ORDER, TCPR_ORDER, TBLPR_ORDER,
    TBLBORDERS_ORDER, LEVEL_ORDER, SETTINGS_ORDER,
    # NEW exports
    PBDR_ORDER, TCMAR_ORDER, TBLCELLMAR_ORDER, NUMBERING_ORDER,
    TR_ORDER, STYLE_ORDER, TBL_ORDER, BODY_ORDER,
    get_local_name, reorder_children, fix_element_order_in_tree, fix_settings,
    # NEW functions
    fix_body_order, wrap_border_elements, fix_table_width_conservative
)
from .business_rules import (
    check_table_grid_consistency,
    check_image_aspect_ratio,
    check_comments_integrity,
    check_section_margins,
    get_image_dimensions
)

__all__ = [
    # constants
    'W_NS', 'W14_NS', 'W15_NS', 'R_NS', 'WP_NS', 'A_NS', 'NS', 'w', 'r',
    # element_order (original)
    'RPR_ORDER', 'PPR_ORDER', 'SECTPR_ORDER', 'TCPR_ORDER', 'TBLPR_ORDER',
    'TBLBORDERS_ORDER', 'LEVEL_ORDER', 'SETTINGS_ORDER',
    # element_order (NEW)
    'PBDR_ORDER', 'TCMAR_ORDER', 'TBLCELLMAR_ORDER', 'NUMBERING_ORDER',
    'TR_ORDER', 'STYLE_ORDER', 'TBL_ORDER', 'BODY_ORDER',
    'get_local_name', 'reorder_children', 'fix_element_order_in_tree', 'fix_settings',
    'fix_body_order', 'wrap_border_elements', 'fix_table_width_conservative',
    # business_rules
    'check_table_grid_consistency', 'check_image_aspect_ratio',
    'check_comments_integrity', 'check_section_margins', 'get_image_dimensions',
    # editing (import via: from docx_lib.editing import ...)
    'editing',
]


# Lazy import for editing module
def __getattr__(name):
    if name == 'editing':
        from . import editing
        return editing
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
