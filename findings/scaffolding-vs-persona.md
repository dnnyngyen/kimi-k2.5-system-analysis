# Slides Agent: Persona Replacement vs. Skill Scaffolding

## Fundamental Difference from Other Agents

The Slides agent operates under a completely different strategy than Docs, Sheets, and Websites agents. This is not a limitation; it is a deliberate architectural choice.

### Group A: Scaffolding Specialists (Docs, Sheets, Websites)

These agents follow the pattern: **OK Computer + Skill Injection**

```
OK Computer Identity ("Kimi is an AI agent...")
    ↓
+ Mandatory Skill Reading
    ├── Sheets: "Must always read the xlsx skill by default"
    ├── Docs: "Must read docx/SKILL.md or pdf/SKILL.md"
    └── Web: "Before ANY frontend project, read webapp-building skill"
    ↓
Result: Pre-primed Generalist with Technical Expertise
```

**Mechanism**: Technical knowledge encoded in `SKILL.md` files. The agent's identity remains unchanged; only the pre-loaded context changes.

### Group B: Persona Replacement (Slides)

The Slides agent replaces the identity entirely:

```
Standard OK Computer Identity ("Kimi is an AI agent...")
    ↓
REPLACED BY
    ↓
McKinsey Consultant Persona ("You are a presentation designer who has worked at McKinsey for 20 years...")
    ↓
Result: Character-Driven Specialist with Style and Voice
```

**Mechanism**: Instead of documentation + skill injection, the agent becomes a *different character* with a specific perspective, taste, and values.

## Why Persona Replacement Instead of Skill Injection?

### The Nature of the Task

**Spreadsheets and Documents**:
- Objective correctness criteria
- Formulas work or they don't
- Compatibility rules are verifiable
- Validation is binary (pass/fail)
- Can be fully documented in SKILL.md

**Presentations**:
- Subjective design criteria
- Aesthetic choices are not binary
- Information density is a judgment call
- Audience impact cannot be validated procedurally
- Cannot be fully specified in documentation

### Technical vs. Creative Knowledge

| Type | Mechanism | Example | Validation |
|------|-----------|---------|-----------|
| **Technical** | SKILL.md documentation | "Use openpyxl to create formulas" | Binary: formula valid or not |
| **Creative** | Persona embodiment | "Think like a McKinsey consultant" | Subjective: is the design compelling? |

Spreadsheet skills can be taught through instruction. Design taste cannot.

## The McKinsey Persona

### Identity Replacement

Rather than instructions, the system prompt establishes a character:

```
"You are a presentation designer who has worked at McKinsey for 20 years,
specializing in creating high-information-density, content-rich, and
in-depth presentation slides for the world's TOP 10 enterprises."
```

This persona embodies:
- **Style**: High-density, structured information presentation
- **Voice**: Authoritative consultant, not assistant
- **Values**: Professional standards, audience expertise awareness
- **Methodology**: McKinsey's approach to visual communication

### What Persona Provides

1. **Aesthetic Direction**: The McKinsey style is distinctive (clean, hierarchical, data-driven)
2. **Workflow Authority**: The agent presents itself as an expert, not a tool
3. **Design Philosophy**: How to balance density, clarity, and impact
4. **Communication Standards**: Tone and structure aligned with consultant expectations

These cannot be encoded as procedures in SKILL.md. They emerge from embodying a character.

## Three-Phase Workflow: Design-Driven

Unlike other agents which follow "technical → validate" flow, Slides follows "design → structure → render":

### Phase 1: Design Analysis (Persona-Driven)

```
User Request
    ↓
As McKinsey Consultant, analyze:
  - Requirements and audience (consultant perspective)
  - Information density strategy (consultant judgment)
  - Visual direction (consultant taste)
  - Color system and typography (consultant standards)
    ↓
Output: Design Document (Markdown)
```

This phase has no SKILL.md equivalent. The agent must *think like a consultant*, not *follow procedure*.

### Phase 2: Content Planning (Persona-Guided)

```
Design Direction Established
    ↓
Information Collection (if needed)
    - Phase 1: Broad research
    - Phase 2: Deep research on selected areas
    ↓
Outline Generation (Interactive)
    - generate_slides_outline tool
    - User confirms/modifies structure
    - User approval before rendering
    ↓
Image Search (Illustration sourcing)
```

The persona guides what counts as "valuable" research and how to structure content.

### Phase 3: Rendering (Technical Execution)

```
Approved Outline + Images
    ↓
Generate HTML (technical)
    - Build slide structure
    - Apply CSS from design system
    - Embed visualizations
    ↓
slides_generator tool (technical)
    - Convert HTML to PPTX
    ↓
Deliver
```

This phase is technical and procedural—similar to other agents' rendering.

## Why This Matters: The Scaffolding vs. Persona Framework

The KIMI system demonstrates a taxonomy for agent specialization:

### When to Use Skill Scaffolding (Docs, Sheets, Web)

Use when:
- Task has objective correctness criteria
- Knowledge can be documented procedurally
- Validation is binary or measurable
- Example: "Spreadsheet formulas must pass validation checks"

**Mechanism**: Inject SKILL.md file with technical procedures

### When to Use Persona Replacement (Slides)

Use when:
- Task has subjective quality criteria
- Knowledge requires judgment and taste
- Validation is qualitative and experience-based
- Example: "Slide design should feel like a consultant created it"

**Mechanism**: Replace identity with expert character

## Key Differences from Skill-Scaffolded Agents

| Aspect | Docs/Sheets/Web | Slides |
|--------|----------------|--------|
| **Strategy** | Skill Injection | Persona Replacement |
| **Base Identity** | OK Computer (unchanged) | McKinsey Consultant (new) |
| **Knowledge Source** | SKILL.md files | Character perspective |
| **Validation** | Binary (pass/fail) | Qualitative (compelling/not) |
| **First Step** | Read SKILL.md | Think like consultant |
| **Correctness Criteria** | Procedural rules | Aesthetic judgment |
| **User Interaction** | Automatic generation | Collaborative approval |

## Architectural Implications

### 1. No SKILL.md File (By Design)

The absence of `/app/.kimi/skills/slides/SKILL.md` is not a gap. It is the *expected outcome* of the persona strategy.

Creating a SKILL.md for presentation design would require:
- Encoding subjective taste as procedures
- Specifying the "McKinsey aesthetic" as rules
- Turning creative judgment into checklists

This is fundamentally impossible. The persona embodies these judgments instead.

### 2. Persona Encodes Expertise

Where Docs agent has:
```
READ: /app/.kimi/skills/docx/SKILL.md (32KB of technical procedures)
```

Slides agent has:
```
BE: A McKinsey consultant with 20 years of presentation experience
```

The second approach distributes expertise through character, not documentation.

### 3. Interactive Approval as Built-In Validation

Other agents generate automatically. Slides includes `generate_slides_outline` tool because:
- Structure is subjective (needs user confirmation)
- Persona-driven outline might not match user intent
- Collaborative approval prevents wasted rendering

This is unique to persona-based agents.

## Theoretical Foundation: Technical vs. Creative Tasks

The KIMI architecture suggests:

**For Technical Tasks**:
- Objective correctness is possible
- Document the rules (SKILL.md)
- Validate procedurally
- Example: XLSX formulas

**For Creative Tasks**:
- Subjective excellence is the goal
- Embody an expert character (Persona)
- Validate through collaboration
- Example: Slide design

This explains why Slides is fundamentally different from other agents—it's not just a different skill, it's a different *kind* of task.

## Conclusion: Infrastructure Innovation

The Slides agent demonstrates **persona replacement** as a specialization strategy:

1. **Not a limitation**: Slides doesn't have a SKILL.md because the task doesn't admit procedural specification
2. **Deliberate architecture**: Using McKinsey persona instead of technical documentation
3. **Different validation**: Qualitative user approval replaces binary checking
4. **Collaborative process**: Interactive outline approval is built-in
5. **Theoretical insight**: Creative tasks require character embodiment, not skill injection

The agent teaches presentation design principles through *being a designer*, not through documentation. This represents a fundamentally different approach to AI specialization than the scaffolding-based agents.

Where Docs says "follow the DOCX rules," Slides says "think like a consultant." The absence of SKILL.md is not a gap; it is the signature of this different paradigm.
