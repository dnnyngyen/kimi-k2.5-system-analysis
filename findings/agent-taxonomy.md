# Analysis of KIMI System Agents and Prompts

## KIMI operates in 8 distinct modes:

# 1. Base KIMI chat (kimi.com/chat):
**KIMI K2.5 Instant** – Fast, non-thinking mode

**KIMI K2.5 Thinking** – Step-by-step reasoning with visible reasoning tokens

**KIMI K2** – Fast, non-thinking mode (deprecated)

**KIMI K2 Thinking** – Step-by-step reasoning with visible reasoning tokens (deprecated)

## 2. KIMI OK Computer & Office Agents:

### 2a. KIMI OK Computer Agent (kimi.com/agent):
Standard single-agent tool use with OK Computer environment. This environment/system prompt is used as the base layer for all other KIMI agents with the exception of KIMI slides, which uses the same environment with a specialized prompt.

### 2b. KIMI Websites (kimi.com/websites):
Standard single-agent tool use with OK Computer environment and KIMI agent prompt with skill reading instructions appended to the end directing it to the webapp skill.

### 2c. KIMI Docs (kimi.com/docs):
Standard single-agent tool use with OK Computer environment and KIMI agent prompt with a document mode activation appended to the end. If a user initiates a KIMI Agent with an uploded doc, it also appends these instructions.

### 2d. KIMI Sheets (kimi.com/sheets):
Standard single-agent tool use with OK Computer environment and KIMI agent prompt with Instructions to read xlsx SKILL.md first

## 3. KIMI Slides (kimi.com/slides):
Standard single-agent tool use with OK Computer environment and a specialized prompt different from the other agents. (More on that in a second.)

## 4. KIMI k1-Researcher (kimi.com/deep-research):
Control flow / Human-in-the-Loop agent for deep research. Runs a specialized model under the hood. (Adding to this repo soon)

## 5. KIMI K2.5 Agent Swarm (kimi.com/agent-swarm):
PARL-trained model capable of orchestrating ~100 agents across ~1.5k steps. (Adding to this repo soon)

---

## Base Chat vs. Kimi Agent (OK Computer)

The same Kimi model powers two different experiences. Base Chat at kimi.com/chat is conversational: 10 tool calls per turn, no skill loading, no persistent filesystem. It's a question-answering system. OK Computer at kimi.com/agent is agentic with runtime skill injection. It produces deliverables.

Both modes run on identical infrastructure: `kernel_server.py` manages the control plane, `jupyter_kernel.py` runs the IPython kernel, and `browser_guard.py` handles Playwright automation. The difference is configuration: tool budgets, skill loading, and workspace paths.

Base Chat can technically do anything OK Computer can do, if you're willing to prompt it carefully enough. It has the same raw tools. But without skill injection, it doesn't know the compatibility gotchas, the validation steps, the styling conventions. You'd have to provide all that context yourself in every conversation.

OK Computer is Base Chat with context pre-loaded. The skill files encode expertise that would otherwise require extensive prompting. The higher tool budget allows complex multi-step workflows. The persistent workspace lets it build things incrementally.

The capability difference isn't about model intelligence; instead, it's about scaffolding. The same model, given the right documentation and enough tool calls, becomes dramatically more capable. This suggests that many perceived differences between AI products are infrastructure differences masquerading as model differences.

---

### OK Computer and the Office Agents

Within the group of KIMI Agents, we see another layer of differentiation. While `OK Computer` serves as the "Generalist" operating system user, Kimi offers four other "Specialized" agents: **Docs**, **Sheets**, **Slides**, and **Web**.

Analyzing the system prompts reveals a distinct split in how these agents are constructed: **Scaffolding vs. Persona**.

### Group A: The Scaffolding Specialists (Docs, Sheets, Web)
**Agents**: Kimi Docs, Kimi Sheets, Kimi Websites.

These agents are essentially **OK Computer with mandatory pre-loaded context**. They share the same identity ("Kimi is an AI agent...") and the same "Communication Guidelines" as the base OK Computer. The difference lies in their **Skill Reading Instructions**:

*   **Kimi Sheets**: The system prompt explicitly mandates: *"Must always read the xlsx skill by default."* It forces the agent to become an Excel expert immediately, skiping the "intent classification" step Ok Computer would usually perform.
*   **Kimi Docs**: Includes mandatory formatting rules (Word vs PDF) that force the reading of `docx/SKILL.md` or `pdf/SKILL.md`.
*   **Kimi Web**: Enforces a strict rule: *"Before starting ANY frontend-related project, you MUST first read the webapp-building skill documentation."*

These agents don't change *who* Kimi is; they just change *what Kimi is focused on*. They are "Pre-primed" generalists.

### Group B: The Persona Replacement (Slides)

**Kimi Slides** breaks this pattern. Instead of adding skills to the OK Computer base, it replaces the identity entirely: 

```
**<ROLE>**
> "You are a presentation designer who has worked at McKinsey for 20 years, specializing in creating high-information-density... presentation slides..."
```

This is **Persona Replacement**. The "McKinsey Consultant" persona is not just a collection of technical rules (like the `xlsx` skill); it embodies a *style*, a *voice*, and a set of *values* (high density, clean structure) that are difficult to encode in a procedural `SKILL.md`.

*   **Technical Skill**: Taught via `SKILL.md` (How to write Python code for Excel).
*   **Creative Taste**: Taught via **Persona** (How to design a slide like a consultant).

This isn't just extra knowledge, it's a different character. The McKinsey persona follows a rigid workflow, communicates more authoritatively, and presents itself as an expert rather than an assistant.

One theory: spreadsheet creation has right answers. Formulas work or they don't. Compatibility rules are objective. You can teach these through documentation. Presentation design requires taste. What makes a slide compelling isn't fully specifiable. You can't write a SKILL.md that explains how to create an emotionally resonant visual argument. But you can ask the model to embody someone who would know.

This pattern suggests thinking about when documentation is sufficient versus when you need something deeper. Technical tasks get skill injection. Creative tasks get persona replacement.

---

### Historical Context: From System Prompts to Modular Skills
The concept of "Skill Injection" represents an evolution of the **System Prompt** architecture, a trend traceable to the work of research labs like **Anthropic** (2023-2026).

*   **2024: The "Be Helpful" Era**: Agents had simple, static system prompts. Capabilities were hard-coded in the model weights (Fine-tuning).
*   **2025: The "Constitutional" Era (Anthropic)**: Anthropic popularized long, structured system prompts ("Constitution") that defined behavior and safety boundaries. This proved that *instruction* could override *training* for behavior control.
*   **2026: The "Skill/Context" Era (Kimi)**: Kimi takes the "Long System Prompt" concept and **shards** it. Instead of one massive 100k token prompt, the capabilities are broken into modular files (`SKILL.md`) that are injected *only when needed*.

This shift allows Kimi to maintain a "clean" base state while accessing "deep" expertise on demand, solving the "Lost in the Middle" problem of massive context windows. Knowledge is separated from identity.

---

## Conclusion

The Kimi architecture suggests a taxonomy for agent development:
1.  **Infrastructure is Intelligence**: Giving a model a persistent filesystem and 300 tool calls (OK Computer) makes it "smarter" than the same model in a chat window (Base Chat).
2.  **Context is Specialization**: You don't need fine-tuning to create a "Sheets Agent"; you just need to force-feed it the right documentation at initialization.
3.  **Persona is for Taste**: When the task is subjective (Design), structural context isn't enough. You need to simulate the *character* of an expert to get the right *vibe*.
