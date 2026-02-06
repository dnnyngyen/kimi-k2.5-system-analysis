# Kimi K2.5 System Analysis

![Kimi K2.5 System Analysis Banner](banner.png)

[![License: Mixed](https://img.shields.io/badge/License-CC0%20%2B%20CC%20BY%204.0-blue)](LICENSE)
[![Type: Research](https://img.shields.io/badge/Type-Research-0366d6)](https://github.com/dnnyngyen/kimi-agent-internals)
[![Method: Conversational Extraction](https://img.shields.io/badge/Method-Conversational%20Extraction-blue)](METHODOLOGY.md)
[![Repo Size](https://img.shields.io/github/repo-size/dnnyngyen/kimi-agent-internals?label=size&color=58a6ff)](https://github.com/dnnyngyen/kimi-agent-internals)
[![Last Commit](https://img.shields.io/github/last-commit/dnnyngyen/kimi-agent-internals?color=79c0ff)](https://github.com/dnnyngyen/kimi-agent-internals/commits/main)

> An analysis of Moonshot AI's Kimi K2.5 agent architecture.
>
> **AI Disclosure:** This analysis was conducted using [Claude Code](https://claude.ai/code).

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [What This Repository Contains](#what-this-repository-contains)
- [Methodology](#methodology)
- [License](#license)

---

## Overview

This is an analysis of Moonshot AI's Kimi K2.5 agent architecture and source code. No authentication was bypassed. No binaries were decompiled. Everything here was provided by the agent itself in response to plain-English questions through standard interfaces.

Kimi shifted from tool-use architectures to skill-based environment architectures. Instead of giving the model discrete APIs, it gives the model general-purpose computing contexts: persistent filesystems, browser automation, and process execution. The model acts as an operating system user rather than an API consumer.

---

## Repository Structure

```
kimi-agent-internals/
├── README.md                 # Main entry point
├── GLOSSARY.md               # Terms and definitions
├── METHODOLOGY.md            # How the analysis was conducted
├── LICENSE                   # Mixed: CC0 + CC BY 4.0 + Apache 2.0
│
├── deep-dives/               # Technical reference documentation
│   ├── README.md
│   ├── architecture/         # System architecture
│   │   ├── container.md
│   │   ├── filesystem.md
│   │   ├── security.md
│   │   └── workspaces.md
│   ├── runtime/              # Runtime components
│   │   ├── browser-automation.md
│   │   ├── code-execution.md
│   │   ├── control-plane.md
│   │   ├── chrome-profile.md
│   │   ├── pdf-viewer.md
│   │   └── utils.md
│   └── binaries/             # Binary analysis
│       └── tectonic.md
│
├── prompts/                  # System prompts for 6 agent types
│   ├── README.md
│   ├── base-chat.md
│   ├── ok-computer.md
│   ├── docs.md
│   ├── sheets.md
│   ├── websites.md
│   ├── slides.md
│   └── memory-format.txt
│
├── analysis/                 # Research findings and analysis
│   ├── README.md
│   ├── execution-flows.md
│   ├── how-kimi-works.md
│   ├── skills-vs-personas.md
│   └── skills/              # Skill system analysis
│       ├── README.md
│       ├── docx/analysis.md
│       ├── pdf/analysis.md
│       ├── webapp/analysis.md
│       └── xlsx/analysis.md
│
├── source-code/       # Extracted source from Kimi system
│   ├── README.md
│   ├── browser_guard.py      # 41KB - Browser automation
│   ├── jupyter_kernel.py     # 17KB - Code execution
│   ├── kernel_server.py      # 10KB - Control plane
│   ├── utils.py              # 1.2KB - Helper functions
│   ├── etc/                  # System configuration (~8KB)
│   │   ├── chromium/         # Chrome security settings
│   │   ├── chromium.d/       # Chrome launch flags
│   │   └── ImageMagick-6/    # Image processing policy
│   ├── pdf-viewer/          # ~4MB - PDF.js Chrome extension (viewer only)
│   │   ├── manifest.json    # Extension manifest (v3)
│   │   └── content/web/     # Viewer core with CJK font support
│   └── skills/              # Skill system source code
│       ├── docx/            # Word document generation
│       │   ├── SKILL.md
│       │   ├── scripts/     # Python/C# toolchain
│       │   ├── assets/templates/  # C# templates
│       │   └── validator/   # .NET validator configs
│       ├── pdf/             # PDF generation
│       ├── xlsx/            # Excel processing
│       └── webapp-building/ # React webapp template
│
└── tools/                    # Tool schemas and documentation
    ├── README.md
    ├── base-chat.json        # Base Chat tool schemas
    ├── ok-computer.json      # OK Computer tool schemas
    ├── base-chat/            # 9 tool docs
    └── ok-computer/          # 29 tool docs
```

---

## Quick Start

| If you want to... | Start here |
|-------------------|------------|
| Understand the architecture | [`analysis/how-kimi-works.md`](analysis/how-kimi-works.md) |
| Learn the terminology | [`GLOSSARY.md`](GLOSSARY.md) |
| Compare agent types | [`prompts/base-chat.md`](prompts/base-chat.md) vs [`prompts/ok-computer.md`](prompts/ok-computer.md) |
| See a skill definition | [`source-code/skills/docx/SKILL.md`](source-code/skills/docx/SKILL.md) |
| Explore technical details | [`deep-dives/README.md`](deep-dives/README.md) |

---

## What This Repository Contains

System prompts for six agent types: Base Chat, OK Computer, Docs, Sheets, Slides, and Websites. Skill definitions for DOCX, XLSX, PDF, and WebApp output formats. Tool schemas documenting 38 distinct tools. [Source code](source-code/) for the runtime environment. Technical analysis of the architecture, security model, and design patterns.

---

## Methodology

This repository contains materials extracted from the Kimi K2.5 agent
environment through its standard public interfaces (kimi.com/agent,
kimi.com/chat, and specialized endpoints). The agent executed shell
commands and file reads in response to conversational queries to
retrieve prompts, source code, and configuration files. No code was
written by the researcher. No authentication was bypassed. No prompt
injection, jailbreaking, or adversarial techniques were used. See
[METHODOLOGY.md](METHODOLOGY.md) for complete details.

**Independent verification:**
- [kimi.com/chat](https://kimi.com/chat) — Base Chat with 10 tool calls
- [kimi.com/agent](https://kimi.com/agent) — OK Computer with full tool access
- [kimi.com/docs](https://kimi.com/docs), [kimi.com/sheets](https://kimi.com/sheets), [kimi.com/slides](https://kimi.com/slides), [kimi.com/websites](https://kimi.com/websites) — Specialized agents

This research is independent and not affiliated with Moonshot AI.

---

## License

This repository uses mixed licensing. Extracted material (prompts, source
code, tool schemas) is released under CC0 1.0 — the maintainer does not
claim copyright over Moonshot AI's work. Original analysis and documentation
is licensed under CC BY 4.0. Third-party components (PDF.js) retain their
upstream licenses. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md)
for details.

---

## Star History

[![GitHub stars](https://img.shields.io/github/stars/dnnyngyen/kimi-agent-internals?style=social)](https://github.com/dnnyngyen/kimi-agent-internals/stargazers)

<a href="https://www.star-history.com/#dnnyngyen/kimi-k2.5-system-analysis&type=date&legend=top-left">
  <img src="https://api.star-history.com/svg?repos=dnnyngyen/kimi-k2.5-system-analysis&type=date&legend=top-left" width="50%">
</a>

