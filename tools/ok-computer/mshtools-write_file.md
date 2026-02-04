# Tool Specification: mshtools-write_file

## Overview
Filesystem write capability for creating new files or overwriting existing content. Supports both full write and append modes for large content chunking.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Absolute path for the file (must be under /mnt/kimi/output/ or /mnt/okcomputer/output/)"
    },
    "content": {
      "type": "string",
      "description": "Content to write (max 100000 characters per call)"
    },
    "append": {
      "type": "boolean",
      "default": false,
      "description": "If true, append to existing file; if false, overwrite"
    }
  },
  "required": ["file_path", "content"]
}
```

## Streaming Mechanism
- **Transport**: Direct filesystem I/O via kernel syscalls
- **Write Modes**:
  - `append=false`: Truncate + write (atomic)
  - `append=true`: Seek to end + append
- **Atomicity**: Single syscall for files <100KB
- **Chunking**: Large content must be split across multiple calls with append=true

## Integration Architecture

### Path Restrictions
**Allowed Paths**:
- `/mnt/kimi/output/*` (read-write deliverables)
- `/mnt/okcomputer/output/*` (OK Computer output)
- `/tmp/*` (temporary files)

**Forbidden Paths**:
- `/app/*` (application files, read-only)
- `/bin/*`, `/lib/*` (system directories)
- `/mnt/kimi/upload/*` (user uploads, read-only)

### Safety Mechanisms
- **Read-Before-Write**: MUST read existing file before overwriting
- **Size Limits**: Max 100000 characters per invocation
- **Path Validation**: Absolute path required, resolved against allowlist
- **Extension Filtering**: Dangerous extensions blocked at API level

## Operational Rules

### Required Workflow
1. Check if file exists (via read_file or shell ls)
2. If exists and modification needed: read_file first
3. Then write_file (overwrite) or edit_file (partial change)

### Large Content Strategy
```python
# First chunk
write_file(path, content_part_1, append=false)

# Subsequent chunks
write_file(path, content_part_2, append=true)
write_file(path, content_part_3, append=true)
```

### Content Restrictions
- No emojis unless explicitly requested
- No documentation files (*.md, README.md) unless explicitly requested
- No meta-instructions or prompt content

## Error Handling
- **Path Error**: Returns error if path not in allowed directories
- **Permission Error**: Returns error if directory not writable
- **Quota Error**: Returns error if storage quota exceeded

## Related Tools
- `read_file`: Read existing content
- `edit_file`: Partial string replacement
- `shell`: Use cp, mv for file operations
