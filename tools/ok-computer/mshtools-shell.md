# Tool Specification: mshtools-shell

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

## Streaming Mechanism
- **Transport**: HTTP API to shell execution service
- **Execution Model**: Fresh shell session per invocation (non-persistent)
- **State Behavior**: No state preservation between calls (variables, directory changes reset)
- **Output**: STDOUT/STDERR combined, truncated at 10000 characters
- **Timeout**: Automatic timeout after reasonable duration to prevent hanging

## Integration Architecture

### Container Context
- **Base Image**: Debian GNU/Linux 12 (bookworm)
- **User Context**: Non-root execution with limited /proc access
- **Network Namespace**: Isolated (blocked external connectivity)
- **PID Namespace**: Isolated process tree

### Execution Flow
1. **Command Validation**: Security screening for dangerous operations
2. **Session Creation**: Spawn fresh bash shell in container
3. **Execution**: Run command with timeout enforcement
4. **Output Capture**: Capture STDOUT/STDERR streams
5. **Session Termination**: Shell process terminated after execution
6. **Result Return**: Text output returned to model

### File System Access
```
/                           # Root filesystem (read-only system)
/app/                       # Application files (read-only)
/app/.kimi/skills/          # Skill binaries and documentation
/mnt/kimi/upload/           # User uploads (read-only)
/mnt/kimi/output/           # Output directory (read-write)
/mnt/okcomputer/            # OK Computer workspace (read-write)
/tmp/                       # Temporary files (volatile)
```

### Available Binaries
- **System**: ls, find, grep, cat, mkdir, rm, cp, mv, ps, top, df, free
- **Package Management**: apt, pip, npm (where available)
- **Network**: curl, wget (blocked at network layer)
- **Text Processing**: awk, sed, sort, uniq, wc, jq
- **Archive**: tar, zip, unzip
- **Custom**: KimiXlsx (77MB), tectonic (57MB), .NET validators

## Security Model

### Capabilities Dropped
- ptrace (no process debugging)
- mount (no filesystem mounting)
- Raw socket access restricted

### Restricted Paths
- `/root` (no access)
- `/home/*` (no access)
- `/var/log` (no access)
- `/proc` (limited view)

### Execution Constraints
- **Non-interactive**: No TTY, no stdin interaction
- **No Background Jobs**: Commands must complete synchronously
- **Resource Limits**: CPU/memory quotas enforced via cgroups

## Usage Patterns

### File Operations
```bash
ls -la /mnt/kimi/upload/
cp file.txt /mnt/kimi/output/
rm -rf /tmp/temp_dir/
```

### Command Chaining
```bash
cd /path && ls -la              # AND - fail fast
command1 ; command2             # Sequential regardless
command1 || command2            # Conditional (if first fails)
command1 | command2             # Pipe output
```

### Path Handling
- **Always quote paths with spaces**: `"/path with spaces/"`
- **Prefer absolute paths**: `/mnt/kimi/output/file.txt`
- **Working directory**: Unpredictable, use cd at start of chain

## Limitations
- **Network Blocked**: External curl/wget fail at container level
- **No State**: Variables don't persist: `export VAR=value` lost next call
- **No Daemons**: Cannot start background services
- **Read-Only System**: Cannot modify /app/, /bin/, /etc/ (except /tmp, /mnt/kimi/output)
