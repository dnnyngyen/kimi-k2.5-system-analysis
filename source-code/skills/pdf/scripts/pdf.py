#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
PDF Processing Tool - Unified Entry Point

Usage:
  pdf.py form info <pdf>                      View form fields
  pdf.py form fill <pdf> -o <out> -d <json>   Fill form
  pdf.py extract text <pdf>                   Extract text
  pdf.py extract table <pdf>                  Extract tables
  pdf.py extract image <pdf> -o <dir>         Extract images
  pdf.py pages merge <pdf>... -o <out>        Merge PDFs
  pdf.py pages split <pdf> -o <dir>           Split PDF
  pdf.py pages rotate <pdf> <deg> -o <out>    Rotate pages
  pdf.py pages crop <pdf> <box> -o <out>      Crop pages
  pdf.py meta get <pdf>                       Read metadata
  pdf.py meta set <pdf> -o <out> -d <json>    Set metadata
  pdf.py convert <file> -o <out>              Convert to PDF
"""

import argparse
import json
import sys
from pathlib import Path

# Add script directory to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

# Output utilities
class Output:
    """Unified output handling"""

    @staticmethod
    def success(data: dict):
        """Success output to stdout"""
        print(json.dumps({"status": "success", "data": data}, ensure_ascii=False, indent=2))
        sys.exit(0)

    @staticmethod
    def error(error: str, message: str, hint: str = None, code: int = 1):
        """Error output to stderr"""
        result = {"status": "error", "error": error, "message": message}
        if hint:
            result["hint"] = hint
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(code)

    @staticmethod
    def check_file(path: str) -> Path:
        """Check if file exists"""
        p = Path(path)
        if not p.exists():
            Output.error("FileNotFound", f"File not found: {path}", code=2)
        return p


# ============ form commands ============
def cmd_form_info(args):
    """View form fields"""
    from cmd_form import form_info
    form_info(args.pdf)


def cmd_form_fill(args):
    """Fill form"""
    from cmd_form import form_fill

    # Parse data
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            Output.error("InvalidJSON", f"JSON parse error: {e}")
    elif args.file:
        try:
            with open(args.file) as f:
                data = json.load(f)
        except Exception as e:
            Output.error("FileError", f"Failed to read file: {e}")
    else:
        Output.error("MissingData", "Requires --data or --file argument")

    form_fill(args.pdf, args.output, data)


# ============ extract commands ============
def cmd_extract_text(args):
    """Extract text"""
    from cmd_extract import extract_text
    extract_text(args.pdf, pages=args.pages)


def cmd_extract_table(args):
    """Extract tables"""
    from cmd_extract import extract_table
    extract_table(args.pdf, pages=args.pages)


def cmd_extract_image(args):
    """Extract images"""
    from cmd_extract import extract_image
    extract_image(args.pdf, args.output)


# ============ pages commands ============
def cmd_pages_merge(args):
    """Merge PDFs"""
    from cmd_pages import pages_merge
    pages_merge(args.pdfs, args.output)


def cmd_pages_split(args):
    """Split PDF"""
    from cmd_pages import pages_split
    pages_split(args.pdf, args.output)


def cmd_pages_rotate(args):
    """Rotate pages"""
    from cmd_pages import pages_rotate
    pages_rotate(args.pdf, args.degrees, args.output, pages=args.pages)


def cmd_pages_crop(args):
    """Crop pages"""
    from cmd_pages import pages_crop
    pages_crop(args.pdf, args.box, args.output, pages=args.pages)


# ============ meta commands ============
def cmd_meta_get(args):
    """Read metadata"""
    from cmd_meta import meta_get
    meta_get(args.pdf)


def cmd_meta_set(args):
    """Set metadata"""
    from cmd_meta import meta_set

    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            Output.error("InvalidJSON", f"JSON parse error: {e}")
    else:
        Output.error("MissingData", "Requires --data argument")

    meta_set(args.pdf, args.output, data)


# ============ convert command ============
def cmd_convert(args):
    """Convert to PDF"""
    from cmd_convert import convert_to_pdf
    convert_to_pdf(args.file, args.output)


# ============ main entry ============
def main():
    parser = argparse.ArgumentParser(
        description="PDF Processing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- form ---
    form_parser = subparsers.add_parser("form", help="Form operations")
    form_sub = form_parser.add_subparsers(dest="subcommand")

    form_info_p = form_sub.add_parser("info", help="View form fields")
    form_info_p.add_argument("pdf", help="PDF file")
    form_info_p.set_defaults(func=cmd_form_info)

    form_fill_p = form_sub.add_parser("fill", help="Fill form")
    form_fill_p.add_argument("pdf", help="Input PDF")
    form_fill_p.add_argument("-o", "--output", required=True, help="Output PDF")
    form_fill_p.add_argument("-d", "--data", help="Field values in JSON format")
    form_fill_p.add_argument("-f", "--file", help="JSON file path")
    form_fill_p.set_defaults(func=cmd_form_fill)

    # --- extract ---
    extract_parser = subparsers.add_parser("extract", help="Content extraction")
    extract_sub = extract_parser.add_subparsers(dest="subcommand")

    extract_text_p = extract_sub.add_parser("text", help="Extract text")
    extract_text_p.add_argument("pdf", help="PDF file")
    extract_text_p.add_argument("-p", "--pages", help="Page range, e.g., 1-3,5")
    extract_text_p.set_defaults(func=cmd_extract_text)

    extract_table_p = extract_sub.add_parser("table", help="Extract tables")
    extract_table_p.add_argument("pdf", help="PDF file")
    extract_table_p.add_argument("-p", "--pages", help="Page range, e.g., 1-3,5")
    extract_table_p.set_defaults(func=cmd_extract_table)

    extract_image_p = extract_sub.add_parser("image", help="Extract images")
    extract_image_p.add_argument("pdf", help="PDF file")
    extract_image_p.add_argument("-o", "--output", default=".", help="Output directory")
    extract_image_p.set_defaults(func=cmd_extract_image)

    # --- pages ---
    pages_parser = subparsers.add_parser("pages", help="Page operations")
    pages_sub = pages_parser.add_subparsers(dest="subcommand")

    pages_merge_p = pages_sub.add_parser("merge", help="Merge PDFs")
    pages_merge_p.add_argument("pdfs", nargs="+", help="PDF files to merge")
    pages_merge_p.add_argument("-o", "--output", required=True, help="Output PDF")
    pages_merge_p.set_defaults(func=cmd_pages_merge)

    pages_split_p = pages_sub.add_parser("split", help="Split PDF")
    pages_split_p.add_argument("pdf", help="PDF file")
    pages_split_p.add_argument("-o", "--output", default=".", help="Output directory")
    pages_split_p.set_defaults(func=cmd_pages_split)

    pages_rotate_p = pages_sub.add_parser("rotate", help="Rotate pages")
    pages_rotate_p.add_argument("pdf", help="PDF file")
    pages_rotate_p.add_argument("degrees", type=int, choices=[90, 180, 270], help="Rotation angle")
    pages_rotate_p.add_argument("-o", "--output", required=True, help="Output PDF")
    pages_rotate_p.add_argument("-p", "--pages", help="Page range, e.g., 1-3,5 (default: all)")
    pages_rotate_p.set_defaults(func=cmd_pages_rotate)

    pages_crop_p = pages_sub.add_parser("crop", help="Crop pages")
    pages_crop_p.add_argument("pdf", help="PDF file")
    pages_crop_p.add_argument("box", help="Crop box left,bottom,right,top (in pt)")
    pages_crop_p.add_argument("-o", "--output", required=True, help="Output PDF")
    pages_crop_p.add_argument("-p", "--pages", help="Page range (default: all)")
    pages_crop_p.set_defaults(func=cmd_pages_crop)

    # --- meta ---
    meta_parser = subparsers.add_parser("meta", help="Metadata operations")
    meta_sub = meta_parser.add_subparsers(dest="subcommand")

    meta_get_p = meta_sub.add_parser("get", help="Read metadata")
    meta_get_p.add_argument("pdf", help="PDF file")
    meta_get_p.set_defaults(func=cmd_meta_get)

    meta_set_p = meta_sub.add_parser("set", help="Set metadata")
    meta_set_p.add_argument("pdf", help="Input PDF")
    meta_set_p.add_argument("-o", "--output", required=True, help="Output PDF")
    meta_set_p.add_argument("-d", "--data", required=True, help="Metadata in JSON format")
    meta_set_p.set_defaults(func=cmd_meta_set)

    # --- convert ---
    convert_parser = subparsers.add_parser("convert", help="Convert to PDF")
    convert_parser.add_argument("file", help="Input file (docx/pptx/xlsx, etc.)")
    convert_parser.add_argument("-o", "--output", help="Output PDF (default: same name)")
    convert_parser.set_defaults(func=cmd_convert)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.parse_args([args.command, "-h"])


if __name__ == "__main__":
    main()
