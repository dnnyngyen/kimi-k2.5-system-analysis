# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================

"""Form operation commands"""

import pikepdf
from pathlib import Path
from pdf import Output


def _get_field_type(field) -> str:
    """Get field type"""
    ft = str(field.get("/FT", ""))
    if ft == "/Tx":
        return "text"
    elif ft == "/Btn":
        # Check if it's a radio button
        ff = int(field.get("/Ff", 0))
        if ff & (1 << 15):  # Radio flag
            return "radio"
        return "checkbox"
    elif ft == "/Ch":
        ff = int(field.get("/Ff", 0))
        if ff & (1 << 17):  # Combo flag
            return "dropdown"
        return "listbox"
    elif ft == "/Sig":
        return "signature"
    return "unknown"


def _get_field_options(field, field_type: str) -> dict:
    """Get field's extra options"""
    options = {}

    if field_type == "checkbox":
        # Get checkbox checked/unchecked values
        ap = field.get("/AP")
        if ap and "/N" in ap:
            states = [str(k) for k in ap["/N"].keys()]
            options["states"] = states
            options["checked_value"] = next((s for s in states if s != "/Off"), states[0] if states else None)

    elif field_type in ("dropdown", "listbox"):
        # Get option list
        opt = field.get("/Opt")
        if opt:
            opts = []
            for item in opt:
                if isinstance(item, list) and len(item) >= 2:
                    opts.append({"value": str(item[0]), "label": str(item[1])})
                else:
                    opts.append({"value": str(item), "label": str(item)})
            options["options"] = opts

    elif field_type == "radio":
        # Radio options are usually in child fields
        kids = field.get("/Kids")
        if kids:
            radio_opts = []
            for kid in kids:
                ap = kid.get("/AP")
                if ap and "/N" in ap:
                    states = [str(k) for k in ap["/N"].keys() if str(k) != "/Off"]
                    if states:
                        radio_opts.append(states[0])
            options["options"] = radio_opts

    return options


def _get_field_value(field) -> str:
    """Get field's current value"""
    v = field.get("/V")
    if v is not None:
        return str(v)
    return None


def _collect_fields(pdf: pikepdf.Pdf) -> list:
    """Collect all form fields"""
    fields = []

    if "/AcroForm" not in pdf.Root:
        return fields

    acroform = pdf.Root.AcroForm
    if "/Fields" not in acroform:
        return fields

    def process_field(field, parent_name=""):
        """Recursively process fields"""
        # Get field name
        name = str(field.get("/T", ""))
        full_name = f"{parent_name}.{name}" if parent_name else name

        # Check for child fields
        kids = field.get("/Kids")
        if kids:
            # If children have /T, recursively process
            has_named_kids = any("/T" in kid for kid in kids)
            if has_named_kids:
                for kid in kids:
                    process_field(kid, full_name)
                return

        # Get field type
        field_type = _get_field_type(field)
        if field_type == "unknown":
            return

        # Build field info
        field_info = {
            "id": full_name,
            "type": field_type,
        }

        # Current value
        current_value = _get_field_value(field)
        if current_value:
            field_info["current_value"] = current_value

        # Extra options
        options = _get_field_options(field, field_type)
        field_info.update(options)

        # Get page number (via /P reference)
        page_ref = field.get("/P")
        if page_ref:
            for i, page in enumerate(pdf.pages):
                if page.objgen == page_ref.objgen:
                    field_info["page"] = i + 1
                    break

        fields.append(field_info)

    for field in acroform.Fields:
        process_field(field)

    return fields


def form_info(pdf_path: str):
    """View form field information"""
    path = Output.check_file(pdf_path)

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    fields = _collect_fields(pdf)

    if not fields:
        Output.success({
            "has_fields": False,
            "count": 0,
            "fields": [],
            "hint": "This PDF has no fillable form fields"
        })

    Output.success({
        "has_fields": True,
        "count": len(fields),
        "fields": fields
    })


def form_fill(pdf_path: str, output_path: str, data: dict):
    """Fill form fields

    data format: {"field_id": "value", ...}
    """
    path = Output.check_file(pdf_path)

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    if "/AcroForm" not in pdf.Root:
        Output.error("NoForm", "This PDF has no form fields")

    acroform = pdf.Root.AcroForm
    if "/Fields" not in acroform:
        Output.error("NoForm", "This PDF has no form fields")

    # Collect existing fields for validation
    existing_fields = {f["id"]: f for f in _collect_fields(pdf)}

    # Validate input data
    errors = []
    for field_id, value in data.items():
        if field_id not in existing_fields:
            errors.append(f"Field not found: {field_id}")
            continue

        field_info = existing_fields[field_id]
        field_type = field_info["type"]

        # Validate checkbox values
        if field_type == "checkbox" and "states" in field_info:
            valid_states = field_info["states"]
            # Allow "true"/"false" as boolean shorthand
            bool_values = ("true", "True", "false", "False", "1", "0")
            if value not in valid_states and f"/{value}" not in valid_states and value not in bool_values:
                errors.append(f"Invalid value for field {field_id}, options: {valid_states} or true/false")

        # Validate dropdown/list values
        if field_type in ("dropdown", "listbox") and "options" in field_info:
            valid_values = [opt["value"] for opt in field_info["options"]]
            if value not in valid_values:
                errors.append(f"Invalid value for field {field_id}, options: {valid_values}")

    if errors:
        Output.error("ValidationError", "Field validation failed", hint="; ".join(errors))

    # Fill fields
    filled_count = 0

    def fill_field(field, parent_name=""):
        nonlocal filled_count
        name = str(field.get("/T", ""))
        full_name = f"{parent_name}.{name}" if parent_name else name

        # Check child fields
        kids = field.get("/Kids")
        if kids:
            has_named_kids = any("/T" in kid for kid in kids)
            if has_named_kids:
                for kid in kids:
                    fill_field(kid, full_name)
                return

        # Fill value
        if full_name in data:
            value = data[full_name]
            field_type = _get_field_type(field)

            if field_type == "checkbox":
                # Checkbox needs /V and /AS
                if value in ("true", "True", "1", True):
                    # Find checked value
                    ap = field.get("/AP")
                    if ap and "/N" in ap:
                        checked = next((str(k) for k in ap["/N"].keys() if str(k) != "/Off"), "/Yes")
                        # pikepdf.Name needs / prefix
                        name_val = checked if checked.startswith("/") else f"/{checked}"
                        field["/V"] = pikepdf.Name(name_val)
                        field["/AS"] = pikepdf.Name(name_val)
                else:
                    field["/V"] = pikepdf.Name("/Off")
                    field["/AS"] = pikepdf.Name("/Off")
            else:
                # Text and other types
                field["/V"] = pikepdf.String(str(value))

            filled_count += 1

    for field in acroform.Fields:
        fill_field(field)

    # Mark for appearance regeneration
    if "/NeedAppearances" not in acroform:
        acroform["/NeedAppearances"] = True

    # Save
    try:
        pdf.save(output_path)
    except Exception as e:
        Output.error("SaveError", f"Save failed: {e}", code=4)

    Output.success({
        "output": output_path,
        "fields_filled": filled_count,
        "fields_requested": len(data)
    })
