#!/usr/bin/env bash
# Unified PDF Skill CLI (aligns with SKILL.md Quick Start)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_SCRIPT="$SCRIPT_DIR/setup.sh"
HTML_SCRIPT="$SCRIPT_DIR/html_to_pdf.js"
LATEX_SCRIPT="$SCRIPT_DIR/compile_latex.py"
PROCESS_SCRIPT="$SCRIPT_DIR/pdf.py"

usage() {
  cat <<'EOF'
Usage: pdf.sh <command> [options]

Commands:
  check [--json]        Run environment diagnostics (setup.sh)
  fix                   Install/repair dependencies (npm playwright, chromium, pip deps)
  html <args...>        Convert HTML to PDF (delegates to html_to_pdf.js)
  latex <args...>       Compile LaTeX with compile_latex.py
  process <args...>     Run python pdf.py process commands (form/extract/pages/...)
EOF
  exit 1
}

append_node_path() {
  local global_root
  if command -v npm &>/dev/null; then
    global_root=$(npm root -g 2>/dev/null || true)
    if [[ -n "$global_root" ]]; then
      if [[ -z "${NODE_PATH:-}" ]]; then
        export NODE_PATH="$global_root"
      elif [[ ":$NODE_PATH:" != *":$global_root:"* ]]; then
        export NODE_PATH="$NODE_PATH:$global_root"
      fi
    fi
  fi
}

cmd_check() {
  set +e
  "$SETUP_SCRIPT" "$@"
  local rc=$?
  set -e
  exit "$rc"
}

cmd_fix() {
  local rc=0

  if command -v npm &>/dev/null; then
    echo "Installing Playwright (global)..."
    if ! npm install -g playwright >/dev/null; then
      echo "Failed to install Playwright via npm."
      rc=3
    fi

    echo "Installing Chromium browser..."
    if ! npx playwright install chromium >/dev/null; then
      echo "Failed to install Chromium via Playwright."
      rc=3
    fi
  else
    echo "npm not found; cannot install Playwright automatically."
    rc=2
  fi

  if command -v python3 &>/dev/null; then
    echo "Installing Python dependencies (pikepdf, pdfplumber)..."
    if ! python3 -m pip install --user -U pikepdf pdfplumber >/dev/null; then
      echo "Failed to install Python dependencies."
      rc=3
    fi
  else
    echo "python3 not found; cannot install PDF processing dependencies."
    rc=2
  fi

  echo "Checking environment after fix..."
  if ! "$SETUP_SCRIPT" >/dev/null; then
    rc=3
  fi

  exit "$rc"
}

cmd_html() {
  if [[ $# -eq 0 ]]; then
    echo "Missing html command arguments."
    usage
  fi
  if ! command -v node &>/dev/null; then
    echo "node not found; run pdf.sh fix first."
    exit 2
  fi
  append_node_path
  if ! node "$HTML_SCRIPT" "$@"; then
    exit 3
  fi
}

cmd_latex() {
  if [[ $# -eq 0 ]]; then
    echo "Missing latex command arguments."
    usage
  fi
  if ! command -v python3 &>/dev/null; then
    echo "python3 not found; run pdf.sh fix first."
    exit 2
  fi
  if ! python3 "$LATEX_SCRIPT" "$@"; then
    exit 3
  fi
}

cmd_process() {
  if [[ $# -eq 0 ]]; then
    echo "Missing process command arguments."
    usage
  fi
  if ! command -v python3 &>/dev/null; then
    echo "python3 not found; run pdf.sh fix first."
    exit 2
  fi
  if ! python3 "$PROCESS_SCRIPT" "$@"; then
    exit 3
  fi
}

main() {
  if [[ $# -lt 1 ]]; then
    usage
  fi

  local command="$1"
  shift || true

  case "$command" in
    check)
      cmd_check "$@"
      ;;
    fix)
      if [[ $# -ne 0 ]]; then
        usage
      fi
      cmd_fix
      ;;
    html)
      cmd_html "$@"
      ;;
    latex)
      cmd_latex "$@"
      ;;
    process)
      cmd_process "$@"
      ;;
    *)
      usage
      ;;
  esac
}

main "$@"
