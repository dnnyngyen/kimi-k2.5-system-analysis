> **Original analysis by the repository maintainer, licensed under CC BY 4.0.**
> Code snippets shown below are excerpted from extracted source code for
> commentary and criticism purposes.

# Workspace Mount Points

Analysis of the filesystem mount points used by Kimi agents.

---

## Overview

Kimi uses two workspace directories depending on the agent mode. Base Chat gets `/mnt/kimi/`. OK Computer and the specialized agents get `/mnt/okcomputer/`.

The Base Chat workspace offers no persistence. Each conversation turn starts fresh. The filesystem is read-only. OK Computer gets full persistence across turns with read-write access and a much larger tool budget.

---

## /mnt/kimi/ (Base Chat)

This is the primary mount point for conversational mode.

**Directory Structure**

```
/mnt/kimi/
├── upload/                # User file uploads (read-only for AI)
├── output/                # AI file outputs (write-only)
└── .store/                # Internal state (citation.jsonl)
```

**Security Model**

The `upload/` directory is writeable by users and readable by the AI. This is where input files live. The `output/` directory is the reverse. Users read from it. The AI writes to it. The `.store/` directory holds internal state like citation tracking. Users cannot access it directly.

**Key Characteristics**

There is no persistence across conversation turns. Each turn starts fresh with a clean slate. The tool budget is limited to 10 steps maximum. The filesystem is read-only. The agent cannot modify uploaded files. The `.store/citation.jsonl` file tracks web sources for citation purposes.

---

## /mnt/okcomputer/ (Agentic Mode)

This is the working directory for specialized agents and OK Computer.

**Directory Structure**

```
/mnt/okcomputer/
├── .todo.jsonl            # Task tracking
├── deploy/                # Deployment artifacts
├── output/                # Generated outputs
│   └── analysis/          # Analysis documents
└── upload/                # User uploads
```

**Key Characteristics**

The filesystem and browser state persist across turns. This enables complex multi-step workflows. The tool budget is 200 to 300 steps. The agent has full read-write access. It can create, modify, and delete files. This directory is the agent's working directory. The `deploy/` subdirectory holds web application deployments.

---

## Comparison

Base Chat targets simple question-answer tasks. OK Computer handles complex multi-step projects. Base Chat gets 10 tool steps. OK Computer gets 200 to 300. Base Chat cannot load skills. OK Computer does this by default.

The Base Chat flow moves from user uploads to the upload directory, through AI processing, to the output directory, then to user downloads. Citation data flows to the `.store/` directory.

The OK Computer flow is more complex. User uploads go to the upload directory. From there the agent branches to output files, deployment artifacts, or task tracking as needed.

---

## Security Implications

The dual-workspace design provides defense in depth. Base Chat isolation limits permissions to prevent accidental damage. Agentic mode capabilities enable complex workflows through full access. The boundaries are clear. Users understand when they are in safe versus powerful modes. There is no cross-contamination. Base Chat cannot access OK Computer files.
