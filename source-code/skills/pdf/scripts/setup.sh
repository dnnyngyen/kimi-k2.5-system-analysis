#!/usr/bin/env bash
# PDF Skill Environment Check
# Usage: setup.sh [--json]
#
# This script checks environment status AND version compatibility.
# It does NOT auto-install anything.
# Agent decides whether to install based on output.
#
# Key checks:
#   1. Required dependencies (node, playwright, chromium, python3, etc.)
#   2. Playwright-Chromium version compatibility (CRITICAL)
#   3. Node.js and Python Playwright version sync (if both installed)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# Dependency Detection
# ============================================================================

check_node() {
    if command -v node &>/dev/null; then
        echo "ok:$(node --version 2>/dev/null | sed 's/v//')"
    else
        echo "missing"
    fi
}

# Get installed Playwright npm version
get_playwright_npm_version() {
    # Try global first
    local ver=$(npm list -g playwright 2>/dev/null | grep playwright@ | sed 's/.*@//' | head -1)
    if [[ -n "$ver" ]]; then
        echo "$ver"
        return
    fi
    # Try npx
    ver=$(npx playwright --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [[ -n "$ver" ]]; then
        echo "$ver"
        return
    fi
    echo ""
}

# Get installed Playwright Python version
get_playwright_python_version() {
    python3 -c "import playwright; print(playwright.__version__)" 2>/dev/null || echo ""
}

# Get Chromium revision from installed browser
get_installed_chromium_revision() {
    local cache=""
    case "$(uname -s)" in
        Darwin) cache="$HOME/Library/Caches/ms-playwright" ;;
        *)      cache="$HOME/.cache/ms-playwright" ;;
    esac

    if [[ ! -d "$cache" ]]; then
        echo ""
        return
    fi

    # Find chromium directories - supports multiple naming conventions:
    #   - chromium-XXXX (older format)
    #   - chrome-XXXX
    #   - chromium_headless_shell-XXXX (newer format)
    # Get the highest revision number
    local revision=$(ls -1 "$cache" 2>/dev/null | grep -oE '(chromium|chrome|chromium_headless_shell)-[0-9]+' | grep -oE '[0-9]+$' | sort -rn | head -1)
    echo "$revision"
}

# Get expected Chromium revision from Playwright
get_expected_chromium_revision() {
    # Run playwright install with dry-run to see what it expects
    local output=$(npx playwright install chromium --dry-run 2>&1 || true)

    # If already installed, it says "chromium-XXXX is already installed" or similar
    # Supports: chromium-XXXX, chrome-XXXX, chromium_headless_shell-XXXX
    local already=$(echo "$output" | grep -oE '(chromium|chrome|chromium_headless_shell)-[0-9]+' | grep -oE '[0-9]+$' | head -1)
    if [[ -n "$already" ]]; then
        echo "$already"
        return
    fi

    # If needs download, extract from "playwright build vXXXX"
    local build=$(echo "$output" | grep -oE 'playwright build v[0-9]+' | sed 's/playwright build v//' | head -1)
    if [[ -n "$build" ]]; then
        echo "$build"
        return
    fi

    echo ""
}

# Verify browser is actually usable by checking executablePath exists
# This is more reliable than directory checks because it uses the same
# require('playwright') resolution that html_to_pdf.js uses
verify_browser_usable() {
    # Require node to be installed
    if ! command -v node &>/dev/null; then
        echo "error:node not installed"
        return
    fi

    local helper="$SCRIPT_DIR/browser_helper.js"
    if [[ ! -f "$helper" ]]; then
        echo "error:helper missing"
        return
    fi

    local output
    output=$(node "$helper" 2>/dev/null)
    local code=$?

    if [[ -z "$output" ]]; then
        if [[ $code -eq 0 ]]; then
            echo "error:unknown"
        else
            echo "error:browser probe failed"
        fi
    else
        echo "$output"
    fi
}

check_playwright() {
    local ver=$(get_playwright_npm_version)
    if [[ -n "$ver" ]]; then
        echo "ok:$ver"
    else
        echo "missing"
    fi
}

check_chromium() {
    local revision=$(get_installed_chromium_revision)
    if [[ -n "$revision" ]]; then
        echo "ok:build-$revision"
    else
        echo "missing"
    fi
}

# Check if Playwright and Chromium versions match
check_playwright_chromium_match() {
    local playwright_ver=$(get_playwright_npm_version)
    if [[ -z "$playwright_ver" ]]; then
        echo "playwright_missing"
        return
    fi

    local installed=$(get_installed_chromium_revision)
    if [[ -z "$installed" ]]; then
        echo "chromium_missing"
        return
    fi

    local expected=$(get_expected_chromium_revision)
    if [[ -z "$expected" ]]; then
        # Can't determine expected version, assume ok if both exist
        echo "ok:unknown"
        return
    fi

    if [[ "$installed" == "$expected" ]]; then
        echo "ok:$installed"
    else
        echo "mismatch:have=$installed,need=$expected"
    fi
}

# Check if Node.js and Python Playwright versions match (if both installed)
check_playwright_versions_sync() {
    local npm_ver=$(get_playwright_npm_version)
    local py_ver=$(get_playwright_python_version)

    if [[ -z "$npm_ver" ]] && [[ -z "$py_ver" ]]; then
        echo "none_installed"
        return
    fi

    if [[ -z "$npm_ver" ]] || [[ -z "$py_ver" ]]; then
        # Only one installed, no sync issue
        echo "ok:single"
        return
    fi

    # Compare major.minor (ignore patch for flexibility)
    local npm_major_minor=$(echo "$npm_ver" | cut -d. -f1,2)
    local py_major_minor=$(echo "$py_ver" | cut -d. -f1,2)

    if [[ "$npm_major_minor" == "$py_major_minor" ]]; then
        echo "ok:$npm_ver"
    else
        echo "mismatch:npm=$npm_ver,python=$py_ver"
    fi
}

check_python() {
    if command -v python3 &>/dev/null; then
        echo "ok:$(python3 --version 2>/dev/null | cut -d' ' -f2)"
    else
        echo "missing"
    fi
}

check_pymod() {
    local mod="$1"
    local ver=$(python3 -c "import $mod; print(getattr($mod, '__version__', 'installed'))" 2>/dev/null)
    if [[ -n "$ver" ]]; then
        echo "ok:$ver"
    else
        echo "missing"
    fi
}

check_libreoffice() {
    local paths=("soffice" "libreoffice" "/Applications/LibreOffice.app/Contents/MacOS/soffice")
    for p in "${paths[@]}"; do
        if command -v "$p" &>/dev/null || [[ -x "$p" ]]; then
            echo "ok"
            return
        fi
    done
    echo "missing"
}

check_tectonic() {
    if command -v tectonic &>/dev/null || [[ -x "$HOME/tectonic" ]]; then
        echo "ok"
    else
        echo "missing"
    fi
}

# ============================================================================
# Status helpers
# ============================================================================

status_is_ok() {
    local status="$1"
    [[ "$status" == ok* ]]
}

status_state() {
    local status="$1"
    if [[ -z "$status" ]]; then
        echo ""
    elif [[ "$status" == *:* ]]; then
        echo "${status%%:*}"
    else
        echo "$status"
    fi
}

status_detail() {
    local status="$1"
    if [[ "$status" == *:* ]]; then
        echo "${status#*:}"
    else
        echo ""
    fi
}

collect_statuses() {
    NODE_STATUS=$(check_node)
    PLAYWRIGHT_STATUS=$(check_playwright)
    CHROMIUM_STATUS=$(check_chromium)
    BROWSER_STATUS=$(verify_browser_usable)
    MATCH_STATUS=$(check_playwright_chromium_match)
    SYNC_STATUS=$(check_playwright_versions_sync)
    PYTHON_STATUS=$(check_python)
    PIKEPDF_STATUS=$(check_pymod pikepdf)
    PDFPLUMBER_STATUS=$(check_pymod pdfplumber)
    LIBREOFFICE_STATUS=$(check_libreoffice)
    TECTONIC_STATUS=$(check_tectonic)
    PLAYWRIGHT_PY_VERSION=$(get_playwright_python_version)
    CHROMIUM_REVISION=$(get_installed_chromium_revision)
}

# ============================================================================
# Output
# ============================================================================

show_status() {
    local name="$1" status="$2" optional="$3"
    local state=$(echo "$status" | cut -d: -f1)
    local detail=$(echo "$status" | cut -d: -f2-)

    if [[ "$state" == "ok" ]]; then
        if [[ "$detail" != "ok" && -n "$detail" ]]; then
            echo "✓ $name ($detail)"
        else
            echo "✓ $name"
        fi
    elif [[ "$state" == "mismatch" ]]; then
        echo "⚠ $name (MISMATCH: $detail)"
    elif [[ "$optional" == "optional" ]]; then
        echo "○ $name (optional, not installed)"
    else
        echo "✗ $name (missing)"
    fi
}

cmd_check() {
    collect_statuses
    local exit_code=0

    echo "=== PDF Skill Environment ==="
    echo ""
    echo "--- HTML Route ---"
    show_status "node" "$NODE_STATUS"
    status_is_ok "$NODE_STATUS" || exit_code=2
    show_status "playwright" "$PLAYWRIGHT_STATUS"
    status_is_ok "$PLAYWRIGHT_STATUS" || exit_code=2
    show_status "chromium" "$CHROMIUM_STATUS"

    # Direct browser usability check (most reliable)
    local browser_state
    browser_state=$(status_state "$BROWSER_STATUS")
    local browser_detail
    browser_detail=$(status_detail "$BROWSER_STATUS")
    local browser_fallback=0

    if [[ "$browser_state" == "ok" ]]; then
        echo "✓ browser executable verified"
    elif [[ "$browser_state" == "fallback" ]]; then
        browser_fallback=1
        echo "✓ browser executable found (existing install)"
        if [[ -n "$browser_detail" ]]; then
            echo "   Path: $browser_detail"
        fi
    elif [[ "$browser_state" == "missing" ]]; then
        echo ""
        echo "⚠️  BROWSER EXECUTABLE NOT FOUND"
        if [[ -n "$browser_detail" ]]; then
            echo "   Expected at: $browser_detail"
        fi
        echo "   Fix: npx playwright install chromium"
        echo ""
        exit_code=2
    elif [[ "$browser_state" == "error" ]]; then
        echo ""
        echo "⚠️  BROWSER CHECK FAILED"
        echo "   Error: $browser_detail"
        echo "   Fix: npm install -g playwright && npx playwright install chromium"
        echo ""
        exit_code=2
    else
        echo ""
        echo "⚠️  Unable to verify browser executable automatically."
        echo "   Falling back to version check..."
        echo ""
    fi

    local match_state
    match_state=$(status_state "$MATCH_STATUS")
    if [[ "$browser_state" == "fallback" ]]; then
        match_state="ok"
    fi
    if [[ "$match_state" == "mismatch" ]]; then
        local details
        details=$(status_detail "$MATCH_STATUS")
        echo ""
        echo "⚠️  PLAYWRIGHT-CHROMIUM VERSION MISMATCH"
        echo "   $details"
        echo "   Fix: npx playwright install chromium"
        echo ""
        if [[ "$browser_state" != "ok" && "$browser_state" != "fallback" ]]; then
            exit_code=2
        fi
    elif [[ "$match_state" == "chromium_missing" && "$browser_state" != "missing" ]]; then
        echo ""
        echo "⚠️  CHROMIUM NOT INSTALLED"
        echo "   Fix: npx playwright install chromium"
        echo ""
        exit_code=2
    elif [[ "$match_state" == "playwright_missing" && "$browser_state" != "error" ]]; then
        echo ""
        echo "⚠️  PLAYWRIGHT NOT INSTALLED"
        echo "   Fix: npm install -g playwright && npx playwright install chromium"
        echo ""
        exit_code=2
    fi

    local sync_state
    sync_state=$(status_state "$SYNC_STATUS")

    if [[ "$sync_state" == "mismatch" ]]; then
        local details
        details=$(status_detail "$SYNC_STATUS")
        echo ""
        echo "⚠️  NODE.JS AND PYTHON PLAYWRIGHT VERSION MISMATCH"
        echo "   $details"
        echo "   This may cause issues if both are used."
        echo "   Fix: Upgrade both to same version, then reinstall chromium:"
        echo "     npm install -g playwright@latest"
        echo "     pip install playwright --upgrade"
        echo "     npx playwright install chromium"
        echo ""
        exit_code=2
    fi

    echo ""
    echo "--- Process Route ---"
    show_status "python3" "$PYTHON_STATUS"
    status_is_ok "$PYTHON_STATUS" || exit_code=2
    show_status "pikepdf" "$PIKEPDF_STATUS"
    status_is_ok "$PIKEPDF_STATUS" || exit_code=2
    show_status "pdfplumber" "$PDFPLUMBER_STATUS"
    status_is_ok "$PDFPLUMBER_STATUS" || exit_code=2

    # Show Python Playwright version if installed
    if [[ -n "$PLAYWRIGHT_PY_VERSION" ]]; then
        echo "  (playwright-python: $PLAYWRIGHT_PY_VERSION)"
    fi

    echo ""
    echo "--- Optional ---"
    show_status "libreoffice" "$LIBREOFFICE_STATUS" optional
    show_status "tectonic" "$TECTONIC_STATUS" optional

    echo ""
    echo "=== Install Commands ==="
    echo "  Node.js:     brew install node (macOS) / apt install nodejs (Ubuntu)"
    echo "  Playwright:  npm install -g playwright && npx playwright install chromium"
    echo "  Python:      brew install python3 (macOS) / apt install python3 (Ubuntu)"
    echo "  pikepdf:     pip install pikepdf pdfplumber --user"
    echo "  LibreOffice: brew install --cask libreoffice (macOS)"
    echo "  Tectonic:    curl -fsSL https://drop-sh.fullyjustified.net | sh"

    echo ""
    echo "=== Fix Version Mismatch ==="
    echo "  npx playwright install chromium   # Reinstall browser to match current Playwright"

    exit "$exit_code"
}

cmd_json() {
    collect_statuses
    local exit_code=0

    cat <<EOF
{
  "html_route": {
    "node": "$(status_state "$NODE_STATUS")",
    "node_version": "$(status_detail "$NODE_STATUS")",
    "playwright": "$(status_state "$PLAYWRIGHT_STATUS")",
    "playwright_version": "$(status_detail "$PLAYWRIGHT_STATUS")",
    "chromium": "$(status_state "$CHROMIUM_STATUS")",
    "chromium_revision": "$CHROMIUM_REVISION",
    "browser_usable": "$(status_state "$BROWSER_STATUS")",
    "browser_path": "$(status_detail "$BROWSER_STATUS")",
    "playwright_chromium_match": "$(status_state "$MATCH_STATUS")",
    "playwright_chromium_detail": "$(status_detail "$MATCH_STATUS")"
  },
  "process_route": {
    "python3": "$(status_state "$PYTHON_STATUS")",
    "python3_version": "$(status_detail "$PYTHON_STATUS")",
    "pikepdf": "$(status_state "$PIKEPDF_STATUS")",
    "pdfplumber": "$(status_state "$PDFPLUMBER_STATUS")",
    "playwright_python_version": "$PLAYWRIGHT_PY_VERSION"
  },
  "version_sync": {
    "node_python_playwright_sync": "$(status_state "$SYNC_STATUS")",
    "sync_detail": "$(status_detail "$SYNC_STATUS")"
  },
  "optional": {
    "libreoffice": "$(status_state "$LIBREOFFICE_STATUS")",
    "tectonic": "$(status_state "$TECTONIC_STATUS")"
  }
}
EOF

    for required in "$NODE_STATUS" "$PLAYWRIGHT_STATUS" "$CHROMIUM_STATUS" "$PYTHON_STATUS" "$PIKEPDF_STATUS" "$PDFPLUMBER_STATUS"; do
        if ! status_is_ok "$required"; then
            exit_code=2
            break
        fi
    done

    local browser_state
    browser_state=$(status_state "$BROWSER_STATUS")
    if [[ "$browser_state" != "ok" ]]; then
        exit_code=2
    fi

    local match_state
    match_state=$(status_state "$MATCH_STATUS")
    if [[ "$match_state" == "mismatch" || "$match_state" == "chromium_missing" || "$match_state" == "playwright_missing" ]]; then
        exit_code=2
    fi

    if [[ "$(status_state "$SYNC_STATUS")" == "mismatch" ]]; then
        exit_code=2
    fi

    exit "$exit_code"
}

# ============================================================================
# Main
# ============================================================================

case "${1:-}" in
    --json|-j)
        cmd_json
        ;;
    -h|--help|help)
        cat <<'EOF'
Usage: setup.sh [options]

Options:
  (none)    Check environment status (default)
  --json    JSON output for programmatic use
  --help    Show this help

This script checks:
  1. Required dependencies (node, playwright, chromium, python3, etc.)
  2. Playwright-Chromium version compatibility (CRITICAL)
  3. Node.js and Python Playwright version sync (if both installed)

If version mismatch is detected, run:
  npx playwright install chromium

The script does NOT enforce specific versions. It only checks that
Playwright and Chromium are compatible with each other.
EOF
        ;;
    *)
        cmd_check
        ;;
esac
