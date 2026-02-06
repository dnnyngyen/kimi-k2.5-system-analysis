# Source Code

> **Extracted material — not authored by this repository's maintainer.**
> These files were provided by the Kimi agent in response to plain-English
> questions about its own environment. They are released under CC0 1.0 to
> the extent of any rights the maintainer may hold. Moonshot AI may hold
> copyright or other rights in this material. See [../LICENSE](../LICENSE).

Extracted Python runtime code for the Kimi K2.5 agent environment.

---

## Table of Contents

- [File Structure](#file-structure)
- [Files](#files)
- [Architecture](#architecture)
- [Security Model](#security-model)
- [Related Documentation](#related-documentation)

---

## File Structure

```
source-code/
├── README.md              # This file
├── browser_guard.py       # 41KB - Browser automation
├── jupyter_kernel.py      # 17KB - Code execution
├── kernel_server.py       # 10KB - Control plane
├── utils.py               # 1.2KB - Helper functions
├── etc/                   # System configuration
│   ├── chromium/          # Chrome browser settings
│   │   └── master_preferences
│   ├── chromium.d/        # Chrome launch flags
│   │   ├── default-flags
│   │   └── extensions
│   └── ImageMagick-6/     # Image processing policy
│       └── policy.xml
├── pdf-viewer/            # ~4MB - PDF.js Chrome extension
│   ├── manifest.json      # Extension manifest (v3)
│   ├── content/web/       # PDF.js viewer core
│   │   ├── cmaps/         # CJK character maps (~50 files)
│   │   ├── standard_fonts/# PDF standard fonts (12 files)
│   │   └── viewer.html    # Main viewer UI
│   └── ...
└── skills/                # Skill system implementation
    ├── docx/              # Word document generation
    │   ├── SKILL.md       # Skill documentation
    │   ├── scripts/       # Python/C# toolchain
    │   ├── assets/templates/  # C# templates
    │   └── validator/     # .NET validator configs
    ├── pdf/               # PDF generation
    ├── xlsx/              # Excel processing
    └── webapp-building/   # React webapp template
```

---

## Files

| File | Size | Description |
|------|------|-------------|
| [`browser_guard.py`](browser_guard.py) | 41KB | Playwright-based browser automation framework. This is the largest module by far. It handles Chromium control, anti-detection measures, and web interaction workflows. See the deep dive in [`../deep-dives/runtime/browser-automation.md`](../deep-dives/runtime/browser-automation.md). |
| [`jupyter_kernel.py`](jupyter_kernel.py) | 17KB | IPython kernel for sandboxed code execution. Manages the ZeroMQ sockets, JSON messaging protocol, and execution loop. Runs as processes 300-400 in the container. Details in [`../deep-dives/runtime/code-execution.md`](../deep-dives/runtime/code-execution.md). |
| [`kernel_server.py`](kernel_server.py) | 10KB | FastAPI control plane for the agent environment. Exposes port 8888 for health checks and kernel lifecycle management. This is how the outer system controls the sandbox. Architecture documented in [`../deep-dives/runtime/control-plane.md`](../deep-dives/runtime/control-plane.md). |
| [`utils.py`](utils.py) | 1.2KB | Shared utility functions. Small but essential helper code used across the other modules. |
| [`etc/`](etc/) | ~8KB | System configuration files. Chrome security policies (search provider, autofill disabled, safe browsing off), ImageMagick resource limits and security policy (PDF/PS formats disabled), browser launch flags. |
| [`pdf-viewer/`](pdf-viewer/) | ~4MB | Mozilla PDF.js Chrome extension for in-browser PDF rendering. Loaded by browser_guard.py with `--load-extension=/app/pdf-viewer`. Contains CJK character maps (~50 files), standard fonts (12 files), ~100 locale files. Independent from the PDF skill. See deep dive: [`../deep-dives/runtime/pdf-viewer.md`](../deep-dives/runtime/pdf-viewer.md). |

---

## Architecture

These four files implement the four-layer container architecture:

```
Layer 1: Control Plane (FastAPI)
├── kernel_server.py (port 8888)
├── Health checks
├── Kernel lifecycle management
└── 10KB Python module

Layer 2: Compute Engine (IPython)
├── jupyter_kernel.py (PID 300-400)
├── ZeroMQ sockets
├── JSON over WebSocket
└── 17KB module

Layer 3: Web Tools (Playwright)
├── browser_guard.py (41KB)
├── Chromium 120.x
└── Ports 9222/9223

Layer 4: User Workspace
├── /mnt/kimi/ (Base Chat)
└── /mnt/okcomputer/ (OK Computer)
```

The control plane manages the compute engine. The compute engine executes user code. The web tools provide browser automation. The workspace provides persistent storage. Each layer depends on the one below it.

---

## Security Model

**Network isolation** blocks external access at the container level. The agent cannot curl google.com directly. All web access goes through the browser tools, which have their own controls.

**Resource limits** enforce a 30-minute timeout and 500MB memory limit. This prevents runaway processes from consuming excessive resources.

**Filesystem restrictions** vary by agent mode. Base Chat gets read-only access. OK Computer gets full read-write access to its workspace.

**Sandboxed execution** isolates all code in a controlled environment. Even if the agent executes malicious Python, it cannot escape the container.

---

## Related Documentation

- [`../deep-dives/runtime/browser-automation.md`](../deep-dives/runtime/browser-automation.md) - Browser guard deep dive
- [`../deep-dives/runtime/code-execution.md`](../deep-dives/runtime/code-execution.md) - Jupyter kernel details
- [`../deep-dives/runtime/control-plane.md`](../deep-dives/runtime/control-plane.md) - Kernel server architecture
- [`../deep-dives/architecture/container.md`](../deep-dives/architecture/container.md) - Four-layer architecture overview
