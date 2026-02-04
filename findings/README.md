# Findings: Key Insights & Analysis

This folder contains the core insights and findings from analyzing the Kimi K2.5 system. Each document builds on the others to provide a comprehensive understanding of how Kimi's agent architecture works.

## Reading Guide

### 1. **[agent-taxonomy.md](agent-taxonomy.md)** - Start Here
**What it covers:** The fundamental difference between two agent types in Kimi:
- **Base Chat**: Traditional tool-use architecture (discrete APIs, narrow scope)
- **OK Computer**: Environment architecture (general-purpose computing, full system access)

**Key takeaway:** This represents a paradigm shift from Tool-Use to Environment-based systems.

---

### 2. **[architecture-overview.md](architecture-overview.md)** - System Design
**What it covers:** How the entire system is structured:
- The "Shell-Operator" paradigm (what agents control)
- Core services (kernel_server, jupyter_kernel, browser_guard)
- Skill system integration
- Data sources and infrastructure

**Key takeaway:** Kimi provides agents with a complete Linux environment + browsers + specialized skills.

**Depends on:** agent-taxonomy.md (understanding agent types)

---

### 3. **[base-chat-vs-okcomputer.md](base-chat-vs-okcomputer.md)** - Comparative Analysis
**What it covers:** Detailed comparison of the two agent types:
- Prompting differences
- Tool capabilities (8 tools vs 23 tools)
- Typical use cases
- Behavioral patterns

**Key takeaway:** Different agents for different tasks; specialized versions inject skills into OK Computer.

**Depends on:** agent-taxonomy.md and architecture-overview.md

---

### 4. **[scaffolding-vs-persona.md](scaffolding-vs-persona.md)** - Specialized Agent Analysis
**What it covers:** Analysis of the Slides agent and persona-based prompting:
- How specialized agents are built (skill injection into base prompts)
- Persona patterns vs generic scaffolding
- Task-specific behavioral tuning

**Key takeaway:** Specialized agents are OK Computer + skill injection + persona tuning.

**Depends on:** base-chat-vs-okcomputer.md

---

## How These Connect

```
agent-taxonomy.md (foundation)
    ↓
    ├→ architecture-overview.md (system design)
    │       ↓
    │   base-chat-vs-okcomputer.md (detailed comparison)
    │       ↓
    │   scaffolding-vs-persona.md (specialized variants)
    │
    └→ [Check reference/ for technical deep-dives]
```

## What's Next?

- **Want to see the prompts?** Go to [../agents/](../agents/)
- **Interested in technical deep-dives?** Check [../reference/](../reference/)
- **Need tool documentation?** See [../tools/](../tools/)
