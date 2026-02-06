#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
LaTeX Compilation Script - Filter logs and report PDF stats

Usage:
    python3 compile_latex.py main.tex
    python3 compile_latex.py main.tex --runs 2
    python3 compile_latex.py main.tex --runs 3 --keep-logs
"""

import argparse
import re
import subprocess
import sys
import os
import shutil
from pathlib import Path

# Log patterns to filter out
FILTER_PATTERNS = [
    r'^note: "version 2" Tectonic command-line interface activated',
    r'^note: Running TeX',
    r'^note: Rerunning TeX because',
    r'^note: Running xdvipdfmx',
    r'^note: downloading ',
    r'^note: Skipped writing .* intermediate files',
]

# Compiled filter regex
filter_regex = re.compile('|'.join(FILTER_PATTERNS))


def find_tectonic():
    """
    Find tectonic executable.
    Priority:
    1. ~/tectonic (user home directory)
    2. tectonic in system PATH
    """
    # Check home directory
    home_tectonic = Path.home() / 'tectonic'
    if home_tectonic.exists() and os.access(home_tectonic, os.X_OK):
        return str(home_tectonic)

    # Check PATH
    tectonic_path = shutil.which('tectonic')
    if tectonic_path:
        return tectonic_path

    return None


def format_size(size_bytes):
    """Format file size to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def extract_pdf_info(pdf_path):
    """
    Extract PDF info: pages, word count, image count.
    Uses pypdf library for accurate statistics.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        # If pypdf not installed, try to install
        print("Installing pypdf library...", file=sys.stderr)
        # Try different install methods
        for install_cmd in [
            [sys.executable, "-m", "pip", "install", "-q", "pypdf"],
            [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "pypdf"],
            [sys.executable, "-m", "pip", "install", "-q", "--user", "pypdf"],
        ]:
            result = subprocess.run(install_cmd, check=False, capture_output=True)
            if result.returncode == 0:
                break

        try:
            from pypdf import PdfReader
        except ImportError:
            return None, None, None

    try:
        reader = PdfReader(pdf_path)

        # Page count
        num_pages = len(reader.pages)

        # Extract text and count words
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Word count (excluding whitespace)
        word_count = len([w for w in text.split() if w.strip()])

        # Image count (count /Image objects)
        image_count = 0
        for page in reader.pages:
            if '/XObject' in page['/Resources']:
                xobjects = page['/Resources']['/XObject'].get_object()
                for obj in xobjects:
                    if xobjects[obj]['/Subtype'] == '/Image':
                        image_count += 1

        return num_pages, word_count, image_count

    except Exception as e:
        print(f"Error extracting PDF info: {e}", file=sys.stderr)
        return None, None, None


def filter_logs(output_lines):
    """
    Filter logs and return:
    - errors list
    - warnings list
    - layout issues list
    - PDF file info line
    """
    errors = []
    warnings = []
    layout_issues = []
    pdf_info_line = None

    for line in output_lines:
        line = line.rstrip()

        # Skip empty lines
        if not line:
            continue

        # Check if line should be filtered
        if filter_regex.match(line):
            # Check for PDF output info
            if line.startswith('note: Writing'):
                pdf_info_line = line
            continue

        # Collect errors
        if line.startswith('error:'):
            errors.append(line)

        # Collect warnings
        elif line.startswith('warning:'):
            warnings.append(line)

        # Collect layout issues (Overfull/Underfull hbox/vbox)
        elif re.search(r'(Overfull|Underfull) \\[hv]box', line):
            layout_issues.append(line)

        # Collect font-related issues
        elif re.search(r'(Font shape|Missing character)', line):
            layout_issues.append(line)

    return errors, warnings, layout_issues, pdf_info_line


def parse_pdf_info_line(line):
    """Parse PDF filename and size from log line"""
    # note: Writing `test1_simple.pdf` (22.77 KiB)
    match = re.search(r"Writing `(.+?)` \((.+?)\)", line)
    if match:
        return match.group(1), match.group(2)
    return None, None


def compile_latex(tex_file, runs=1, keep_logs=False):
    """
    Compile LaTeX file.

    Args:
        tex_file: TeX file path
        runs: Number of compilation runs (for cross-references)
        keep_logs: Whether to keep full logs
    """
    tex_path = Path(tex_file)

    if not tex_path.exists():
        print(f"✗ Error: File not found {tex_file}")
        return 1

    print(f"Compiling {tex_path.name}...", flush=True)
    if runs > 1:
        print(f"Running {runs} passes (for cross-references)", flush=True)

    # Collect all compilation output
    all_output = []
    success = False

    # Find tectonic command
    tectonic_cmd = find_tectonic()
    if not tectonic_cmd:
        print("\n✗ Error: tectonic command not found")
        print("Please install tectonic: https://tectonic-typesetting.github.io/")
        print("\nHint: If installed at ~/tectonic, ensure it has execute permission:")
        print("  chmod +x ~/tectonic")
        return 1

    # Multiple compilation passes
    for run in range(runs):
        try:
            result = subprocess.run(
                [tectonic_cmd, '-X', 'compile', str(tex_path)],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            # Merge stdout and stderr
            output = result.stdout + result.stderr
            all_output.extend(output.splitlines())

            if result.returncode == 0:
                success = True
            else:
                success = False
                break

        except subprocess.TimeoutExpired:
            print("\n✗ Error: Compilation timeout (>2 minutes)")
            return 1
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return 1

    # If user requested full logs
    if keep_logs:
        print("\n" + "="*50)
        print("Full logs:")
        print("="*50)
        for line in all_output:
            print(line)
        print("="*50 + "\n")

    # Filter logs
    errors, warnings, layout_issues, pdf_info_line = filter_logs(all_output)

    # Parse PDF info
    pdf_filename = None
    pdf_size_str = None
    if pdf_info_line:
        pdf_filename, pdf_size_str = parse_pdf_info_line(pdf_info_line)

    # If filename not found in logs, infer from input
    if not pdf_filename:
        pdf_filename = tex_path.stem + '.pdf'

    pdf_path = tex_path.parent / pdf_filename

    # Output results
    print()
    if success:
        if warnings or layout_issues:
            print("✓ Compilation successful (with warnings)")
        else:
            print("✓ Compilation successful")
    else:
        print("✗ Compilation failed")

    # Output PDF info
    if success and pdf_path.exists():
        print()
        print("========================")
        print("PDF Information")
        print("========================")
        print(f"File: {pdf_filename}")

        # File size
        if pdf_size_str:
            print(f"Size: {pdf_size_str}")
        else:
            size = pdf_path.stat().st_size
            print(f"Size: {format_size(size)}")

        # Extract page count, word count, image count
        num_pages, word_count, image_count = extract_pdf_info(str(pdf_path))

        if num_pages is not None:
            print(f"Pages: {num_pages}")
        if word_count is not None:
            print(f"Words: ~{word_count:,}")
        if image_count is not None:
            print(f"Images: {image_count}")

    # Output layout issues
    if layout_issues:
        print()
        print("========================")
        print(f"Layout Issues ({len(layout_issues)})")
        print("========================")
        for issue in layout_issues:
            print(issue)

    # Output warnings
    if warnings:
        print()
        print("========================")
        print(f"Warnings ({len(warnings)})")
        print("========================")
        for warning in warnings:
            # Remove "warning: " prefix
            clean_warning = warning.replace('warning: ', '', 1)
            print(clean_warning)

    # Output errors
    if errors:
        print()
        print("========================")
        print("Errors")
        print("========================")
        for error in errors:
            # Remove "error: " prefix
            clean_error = error.replace('error: ', '', 1)
            print(clean_error)

    # Output system reminder
    if success and (layout_issues or warnings):
        print()
        print("<system-reminder>")
        print(f"Detected {len(layout_issues)} layout issues and {len(warnings)} warnings.")
        print("These issues affect PDF typesetting quality and must be fixed.")
        print("Do not dismiss with 'warnings don't affect output'. Fix all issues.")
        print("</system-reminder>")

    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(
        description='Compile LaTeX file, filter logs, and report PDF stats'
    )
    parser.add_argument('tex_file', help='TeX file path')
    parser.add_argument('--runs', type=int, default=1,
                       help='Number of compilation runs (for cross-references, default: 1)')
    parser.add_argument('--keep-logs', action='store_true',
                       help='Keep full compilation logs')

    args = parser.parse_args()

    return compile_latex(args.tex_file, args.runs, args.keep_logs)


if __name__ == '__main__':
    sys.exit(main())
