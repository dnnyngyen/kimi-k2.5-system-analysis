> **Original documentation by the repository maintainer, licensed under CC BY 4.0.**
> Extracted system prompt text is in the individual prompt files, licensed under CC0 1.0.

# System Prompts

This directory contains the system prompts for all 6 Kimi K2.5 agent types.

---

## Table of Contents

- [File Structure](#file-structure)
- [Agent Hierarchy](#agent-hierarchy)
- [The Two Base Prompts](#the-two-base-prompts)
- [Specialized Agents](#specialized-agents)
- [Skill Loading Process](#skill-loading-process)
- [Key Differences Summary](#key-differences-summary)
- [Reading Order](#reading-order)
- [Related Documentation](#related-documentation)

---

## File Structure

```
prompts/
├── README.md           # This file
├── base-chat.md        # Base Chat foundation prompt
├── ok-computer.md      # OK Computer agentic prompt
├── docs.md             # Docs Agent (DOCX skill)
├── sheets.md           # Sheets Agent (XLSX skill)
├── websites.md         # Websites Agent (WebApp skill)
├── slides.md           # Slides Agent (McKinsey persona)
└── memory-format.txt   # Memory storage format
```

---

## Agent Hierarchy

```
                    ┌─────────────────────────────────────┐
                    │         USER REQUEST                │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │      INTENT CLASSIFICATION          │
                    │  (What does the user want?)         │
                    └─────────────┬───────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   SIMPLE QUERY  │ │  COMPLEX TASK   │ │ SPECIFIC FORMAT │
    │                 │ │                 │ │                 │
    │  "What's the    │ │  "Research and  │ │  "Create a      │
    │   weather?"     │ │   build a web   │ │   document"     │
    │                 │ │   app"          │ │                 │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   BASE CHAT     │ │  OK COMPUTER    │ │  SKILL-ENABLED  │
    │                 │ │                 │ │  AGENTS         │
    │  • 10-step      │ │  • 200-300 step │ │                 │
    │    budget       │ │    budget       │ │  • Docs Agent   │
    │  • No skills    │ │  • Skill loading│ │  • Sheets Agent │
    │  • Read-only FS │ │  • Full FS      │ │  • Slides Agent │
    │                 │ │                 │ │  • Websites     │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
                                  ▲                   │
                                  │                   │
                                  └───────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
          ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
          │ SKILL SCAFFOLD  │  │ SKILL SCAFFOLD  │  │ PERSONA REPLACE │
          │                 │  │                 │  │                 │
          │ OK Computer +   │  │ OK Computer +   │  │ McKinsey        │
          │ DOCX skill      │  │ XLSX skill      │  │ consultant      │
          │                 │  │                 │  │ persona         │
          └─────────────────┘  └─────────────────┘  └─────────────────┘
                 Docs Agent          Sheets Agent          Slides Agent

          ┌─────────────────┐  ┌─────────────────┐
          │ SKILL SCAFFOLD  │  │ SKILL SCAFFOLD  │
          │                 │  │                 │
          │ OK Computer +   │  │ OK Computer +   │
          │ WebApp skill    │  │ PDF skill       │
          │                 │  │                 │
          └─────────────────┘  └─────────────────┘
               Websites Agent        (implied)
```

---

## The Two Base Prompts

### [base-chat.md](base-chat.md)

The foundation for all agent interactions. Defines Kimi's core identity as a helpful AI assistant with specific constraints:
- 10-step budget limit
- Read-only filesystem access (`/mnt/kimi/`)
- No persistence across turns
- 9 core tools (web search, ipython, shell, etc.)

Key behavioral instruction: *"You are an AI assistant with a strong attention to detail and a commitment to following instructions precisely."*

### [ok-computer.md](ok-computer.md)

The agentic generalist prompt. Extends Base Chat with:
- 200-300 step budget
- Full filesystem read-write (`/mnt/okcomputer/`)
- Persistence across turns
- 28+ tools including browser automation
- Skill loading capability

Key behavioral instruction: *"You are an advanced AI agent capable of complex multi-step tasks. You have access to a persistent environment where state is maintained across interactions."*

---

## Specialized Agents

### [docs.md](docs.md)

**Pattern**: Skill Scaffolding
**Base**: OK Computer prompt
**Addition**: DOCX skill documentation prepended

Activates when document generation is detected. Instructs the agent on C# OpenXML SDK usage, document structure, and validation requirements.

### [sheets.md](sheets.md)

**Pattern**: Skill Scaffolding
**Base**: OK Computer prompt
**Addition**: XLSX skill documentation prepended

Activates for spreadsheet tasks. Includes guidance on the 77MB KimiXlsx validator, pivot tables, and Excel-specific formatting.

### [websites.md](websites.md)

**Pattern**: Skill Scaffolding
**Base**: OK Computer prompt
**Addition**: WebApp skill documentation prepended

Activates for web application requests. Uses React + TypeScript + shadcn/ui stack with deployment to dynamic subdomains.

### [slides.md](slides.md)

**Pattern**: Persona Replacement
**Base**: Complete McKinsey consultant persona
**Addition**: N/A (replaces OK Computer entirely)

**Architecturally distinct**: Unlike other specialized agents, Slides does not use OK Computer + skill scaffolding. Instead, it replaces the entire base prompt with an expert presentation designer persona ("20 years of experience at McKinsey").

This shows a fundamental design decision: **technical tasks get skill documentation; creative tasks get expert personas.**

---

## Skill Loading Process

```
User: "Create a Word document about climate change"
          │
          ▼
┌─────────────────────────┐
│ Intent Classification   │
│ Detects: DOCX format    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Load DOCX SKILL.md      │
│ Prepend to context      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Context Stack:          │
│ 1. DOCX skill (top)     │
│ 2. OK Computer base     │
│ 3. User message         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Agent executes with     │
│ skill knowledge loaded  │
└─────────────────────────┘
```

---

## Key Differences Summary

**Base Chat** uses the base prompt only with a 10-step budget, no persistence, no skill loading, 9 tools, and read-only filesystem access.

**OK Computer** uses the base prompt only with a 200-300 step budget, full persistence, dynamic skill loading, 28 plus tools, and read-write filesystem access.

**Docs, Sheets, and Websites** use skill scaffolding on top of OK Computer with a 200-300 step budget, full persistence, pre-loaded skills, 28 plus tools, and read-write filesystem access.

**Slides** uses persona replacement instead of skill scaffolding with a 200-300 step budget, full persistence, 28 plus tools, and read-write filesystem access.

---

## Reading Order

1. Start with `base-chat.md` to understand the foundation
2. Compare with `ok-computer.md` to see the agentic extensions
3. Read `docs.md` to see skill scaffolding in action
4. Read `slides.md` to see persona replacement
5. Note how `sheets.md` and `websites.md` follow the same scaffolding pattern as `docs.md`

---

## Related Documentation

- [`../analysis/skills/README.md`](../analysis/skills/README.md) - How skills work
- [`../tools/README.md`](../tools/README.md) - Tools available to these agents
- [`../analysis/how-kimi-works.md`](../analysis/how-kimi-works.md) - Full architecture analysis
- [`../analysis/skills-vs-personas.md`](../analysis/skills-vs-personas.md) - Why Slides is different
