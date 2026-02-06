> **Original documentation by the repository maintainer, licensed under CC BY 4.0.**

# Deep Dives

Technical reference documentation for the Kimi K2.5 runtime environment.

These documents contain detailed implementation analysis extracted from the container filesystem and source code.

---

## Table of Contents

- [File Structure](#file-structure)
- [Architecture](#architecture)
- [Runtime](#runtime)
- [Binaries](#binaries)
- [Reading Guide](#reading-guide)
- [Related Documentation](#related-documentation)

---

## File Structure

```
deep-dives/
├── README.md                 # This file
├── architecture/             # System architecture
│   ├── container.md          # Four-layer container architecture
│   ├── filesystem.md         # Complete filesystem inventory
│   ├── security.md           # Security model analysis
│   └── workspaces.md         # Mount point analysis
├── runtime/                  # Runtime components
│   ├── browser-automation.md # browser_guard.py analysis
│   ├── code-execution.md     # jupyter_kernel.py analysis
│   ├── control-plane.md      # kernel_server.py analysis
│   ├── chrome-profile.md     # Chrome data directory analysis
│   ├── pdf-viewer.md         # PDF.js extension analysis
│   └── utils.md              # Utility functions
└── binaries/                 # Binary analysis
    └── tectonic.md           # LaTeX compiler analysis
```

---

## Architecture

| Document | Description |
|----------|-------------|
| [`architecture/container.md`](architecture/container.md) | Four-layer container architecture: control plane, compute engine, web tools, and user workspace. Includes service ports, binary analysis, and security model. |
| [`architecture/filesystem.md`](architecture/filesystem.md) | Complete filesystem inventory. Directory structures, file counts, permission zones, and mount points. |
| [`architecture/security.md`](architecture/security.md) | Security model analysis. Sandbox boundaries, network isolation, authentication gaps, and risk assessment. |
| [`architecture/workspaces.md`](architecture/workspaces.md) | Mount point analysis. /mnt/kimi/ versus /mnt/okcomputer/, persistence models, and access controls. |

---

## Runtime

| Document | Description |
|----------|-------------|
| [`runtime/browser-automation.md`](runtime/browser-automation.md) | browser_guard.py analysis. Playwright and Chrome DevTools Protocol implementation, stealth mode, anti-detection measures. |
| [`runtime/code-execution.md`](runtime/code-execution.md) | jupyter_kernel.py analysis. IPython kernel, ZeroMQ messaging, execution budgets, resource limits. |
| [`runtime/control-plane.md`](runtime/control-plane.md) | kernel_server.py analysis. FastAPI endpoints, kernel lifecycle management, health checks. |
| [`runtime/chrome-profile.md`](runtime/chrome-profile.md) | Chrome data directory analysis. Cookie storage, browsing history, extension state, security implications. |
| [`runtime/pdf-viewer.md`](runtime/pdf-viewer.md) | PDF.js extension analysis. Chrome extension structure, permissions, CJK font support. |
| [`runtime/utils.md`](runtime/utils.md) | Utility functions. Shared helper code used across modules. |

---

## Binaries

| Document | Description |
|----------|-------------|
| [`binaries/tectonic.md`](binaries/tectonic.md) | LaTeX compiler analysis. 57MB binary, XeTeX engine, automatic package management. |

---

## Reading Guide

Start with [`architecture/container.md`](architecture/container.md) for the overall system picture, then explore specific runtime components based on your interest.

For the skill system and agent behavior, see [`../analysis/skills/README.md`](../analysis/skills/README.md) and [`../analysis/how-kimi-works.md`](../analysis/how-kimi-works.md).

---

## Related Documentation

- [`../source-code/README.md`](../source-code/README.md) - Python source files analyzed in these deep dives
- [`../analysis/skills/README.md`](../analysis/skills/README.md) - Skill system documentation
- [`../analysis/how-kimi-works.md`](../analysis/how-kimi-works.md) - Architectural overview
