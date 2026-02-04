# Artifacts: Primary Sources

This folder contains extracted primary sources: Python source code and skill definitions.

**Note:** Agent system prompts and tool definitions are now located at the top level in the [`../agents/`](../agents/) directory.

## Organization

### [../agents/](../agents/) - Agent Configurations (Top Level)

For agent prompts, system instructions, and how they're organized, see the top-level `agents/` directory:
- 6 agent types: Base Chat, OK Computer, Docs, Sheets, Slides, Websites
- Each has `prompt.md`, `README.md`, and optional `memory.txt`

For tool documentation (8 tools for Base Chat, 31 mshtools for OK Computer), see [`../tools/`](../tools/)

---

---

### [source/](source/) - Extracted Python Code

Core system components:

- `browser_guard.py` (41KB) - Browser automation & control system
- `jupyter_kernel.py` (17KB) - Jupyter kernel interface
- `kernel_server.py` (10KB) - Server managing the kernel
- `utils.py` (1.2KB) - Utility functions

---

## Understanding the Architecture

### Agent Hierarchy

```
┌─────────────────────────────────────────────────┐
│                   BASE CHAT                      │
│  (Traditional tool-use: search, data, shell)    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                 OK COMPUTER                      │
│  (Environment arch: full system + browser)      │
│                                                 │
│  ├─ Base Prompt (generic Linux environment)    │
│  └─ 23 Tools (browser, file, generation, etc)  │
└─────────────────────────────────────────────────┘
         ↓ (skill injection)
    ┌────────────────────────────────────────┐
    │  Specialized Agents                    │
    │                                        │
    │  ├─ Docs (+ docx-skill)               │
    │  ├─ Sheets (+ xlsx-skill)             │
    │  ├─ Slides (+ slides-skill)           │
    │  └─ Websites (+ webapp-skill)         │
    └────────────────────────────────────────┘
```

### Tool Sharing

- **Base Chat tools (8):** Independent set, unique to base chat
- **OK Computer tools (23):** Shared across:
  - OK Computer itself
  - Docs agent
  - Sheets agent
  - Slides agent
  - Websites agent

All specialized agents use the same 23 tools, but their system prompts differ to guide behavior toward their specific skill.

---

## Skills Definitions

The `skills/` subdirectory contains SKILL.md definitions for each skill system:
- `docx/SKILL.md` - DOCX skill definition
- `pdf/SKILL.md` - PDF skill definition
- `webapp/SKILL.md` - WebApp skill definition
- `xlsx/SKILL.md` - XLSX skill definition

For detailed skill analysis and workflows, see [`../reference/docx-skill/`](../reference/docx-skill/), [`../reference/pdf-skill/`](../reference/pdf-skill/), etc.

---

## How to Use This Folder

1. **Want to understand how agents work?** Start with [`../agents/*/prompt.md`](../agents/)
2. **What can agents do?** Each agent has a prompt with tool capabilities
3. **How do specific tools work?** See [`../tools/base-chat/`](../tools/base-chat/) or [`../tools/ok-computer/`](../tools/ok-computer/)
4. **Want to see actual code?** Browse [`source/`](source/)
5. **Need skill definitions?** See [`skills/*/SKILL.md`](skills/)

---

## Cross-References

- **For agent comparisons:** See [`../findings/base-chat-vs-okcomputer.md`](../findings/base-chat-vs-okcomputer.md)
- **For skill analysis & workflows:** See [`../reference/`](../reference/) (docx-skill/, pdf-skill/, webapp-skill/, xlsx-skill/)
- **For system architecture:** See [`../findings/architecture-overview.md`](../findings/architecture-overview.md)
- **For agent prompts:** See [`../agents/`](../agents/)
