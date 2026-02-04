# Tool specification: shell (Base Chat)

## Overview
Bash command execution in non-persistent environment providing system-level access to Debian GNU/Linux 12 (bookworm) container. Enables file operations, package management, and binary execution.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "Shell command to execute (single command or chained with &&, ;, ||, |)"
    }
  },
  "required": ["command"]
}
```

## Architectural Position

The shell tool is **not merely a command executor**—it is the **primary interface to the containerized operating system**. It provides the bridge between the LLM's cognitive space and the actual computation environment.

## System Architecture

### Container Context
The shell operates within a 4-layer architecture:
1. Control Plane (kernel_server.py:8888)
2. Compute Engine (jupyter_kernel.py)
3. Web Tools (browser_guard.py + Chromium)
4. User Workspace (/mnt/kimi/, /mnt/okcomputer/)

### Execution Model
- **Non-persistent**: Fresh bash process per invocation
- **No state carryover**: Environment variables, aliases reset
- **Command chaining**: &&, ;, ||, | execute in same session
- **Timeout**: Hard limit prevents infinite loops

## Network Isolation

The container implements network isolation at the namespace level:
- External connectivity blocked for all processes equally
- Python requests, Node.js HTTPS, Chrome navigation, curl all fail
- Internal localhost permitted (port 8888, 9222, 9223)

**Exception**: Browser tools route through browser_guard.py → Chrome proxy with separate network handling.

## Binary Ecosystem

### Core Infrastructure
| Binary | Size | Purpose |
|--------|------|---------|
| dotnet | ~150MB | C# compiler/runtime (DOCX) |
| tectonic | 57MB | LaTeX compiler (PDF) |
| node | ~80MB | JavaScript runtime (PDF, WebApp) |
| python3 | ~50MB | Interpreter (universal) |

### Skill Binaries
| Binary | Size | Function |
|--------|------|----------|
| KimiXlsx | 77MB | Excel validation (XLSX) |
| Validator | 73KB | OpenXML validation (DOCX) |
| html_to_pdf.js | 600 lines | PDF conversion |

## Shell as Orchestrator

### Build Pipeline (DOCX)
```bash
./scripts/docx build output.docx
# 1. dotnet build
# 2. dotnet run
# 3. python3 fix_element_order.py
# 4. ./validator/Validator
# 5. python3 validate_docx.py
# 6. pandoc verification
```

### Validation Gate (XLSX)
```bash
KimiXlsx recheck output.xlsx
if [ $? -ne 0 ]; then exit 1; fi
```

## Security Model

### Capabilities Dropped
- SYS_PTRACE (no debugging)
- SYS_ADMIN (no admin)
- NET_RAW (no raw sockets)
- MKNOD (no device creation)

### User Context
Non-root execution with limited /proc access.

## Performance

### Cold vs Warm
- dotnet build: 3-5s cold, 1-2s warm
- npm install: 30-60s cold, instant warm
- KimiXlsx: 500ms cold, 200ms warm

### Resource Limits
- CPU: 2 cores
- Memory: 4GB RAM
- Disk: No persistent storage except output dirs

## Summary

Shell is the **foundation of system interaction**:
- Compilation (dotnet, tectonic, node)
- Validation (custom binaries)
- Orchestration (chaining tools)
- Exploration (filesystem navigation)
- Debugging (process monitoring)
