# Tool Specification: mshtools-todo_read

## Overview
Task list retrieval tool with no parameters. Returns current todo items with status, priority, and content for session state awareness.

## JSON Schema
```json
{
  "type": "object",
  "properties": {}
}
```

## Streaming Mechanism
- **Storage Location**: `/mnt/kimi/.store/.todo.jsonl`
- **Return Format**:
  ```json
  {
    "todos": [
      {
        "id": "1",
        "content": "Task description",
        "status": "in_progress",
        "priority": "high"
      }
    ]
  }
  ```
- **Empty State**: Returns empty list if no todos exist

## Integration Architecture

### Persistence
- **File**: `/mnt/kimi/.store/.todo.jsonl` (append-only)
- **Scope**: Session-scoped (survives kernel restarts but not new conversations)
- **Size**: ~634 bytes typical

## Usage Patterns

### Check Status
```
todo_read()  # No parameters
# Returns current task list
```

### Workflow Integration
- At conversation start to check pending work
- Before starting new tasks to prioritize
- When user asks about previous tasks
- After completing tasks to update understanding
- Every few messages to ensure on track
