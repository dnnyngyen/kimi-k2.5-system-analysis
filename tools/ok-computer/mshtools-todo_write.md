# Tool Specification: mshtools-todo_write

## Overview
Structured task list management system for tracking progress, organizing complex tasks, and maintaining state across multi-step operations. Creates hierarchical todo lists with status tracking.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "todos": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique identifier for the task"
          },
          "content": {
            "type": "string",
            "description": "Task description"
          },
          "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed"],
            "description": "Current status of the task"
          },
          "priority": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Task priority level"
          }
        },
        "required": ["id", "content", "status", "priority"]
      }
    }
  },
  "required": ["todos"]
}
```

## Streaming Mechanism
- **Transport**: Direct state update to session storage
- **Persistence**: Stored in `/mnt/kimi/.store/.todo.jsonl` (634 bytes typical)
- **Update Model**: Full replacement of todo list (not incremental)
- **Access**: Read via `todo_read` (no parameters required)

## Integration Architecture

### Storage Layer
- **Path**: `/mnt/kimi/.store/.todo.jsonl`
- **Format**: JSON Lines (append-only log)
- **Scope**: Session-scoped (persists across turns but not conversations)
- **Size**: ~634 bytes typical

### State Management
```python
# Internal representation
{
  "todos": [
    {
      "id": "1",
      "content": "Initialize project",
      "status": "completed",
      "priority": "high"
    },
    {
      "id": "2", 
      "content": "Build components",
      "status": "in_progress",
      "priority": "high"
    }
  ]
}
```

## Operational Rules

### When to Use
- Complex multi-step tasks (3+ distinct actions)
- Non-trivial tasks requiring planning
- User explicitly requests todo list
- Multiple tasks (numbered or comma-separated)
- After receiving new instructions

### When NOT to Use
- Single straightforward task
- Trivial tasks (<3 steps)
- Purely conversational tasks

### Task States
- **pending**: Not started
- **in_progress**: Currently working (only ONE at a time allowed)
- **completed**: Finished successfully

### Management Rules
- Update status live while working
- Complete tasks immediately after finishing
- Don't batch completions
- Remove irrelevant tasks
- Mark as completed only when: fully accomplished, no errors, final implementation, dependencies found

## Usage Patterns

### Creating Initial List
```json
{
  "todos": [
    {"id": "1", "content": "Read skill documentation", "status": "completed", "priority": "high"},
    {"id": "2", "content": "Create project structure", "status": "in_progress", "priority": "high"},
    {"id": "3", "content": "Implement features", "status": "pending", "priority": "medium"}
  ]
}
```

### Updating Progress
```json
{
  "todos": [
    {"id": "1", "content": "Read skill documentation", "status": "completed", "priority": "high"},
    {"id": "2", "content": "Create project structure", "status": "completed", "priority": "high"},
    {"id": "3", "content": "Implement features", "status": "in_progress", "priority": "medium"}
  ]
}
```

## System Integration
- **OK Computer Only**: Not available in Base Chat
- **Proactive Use**: System encourages frequent checking via `todo_read`
- **Workflow Integration**: Used at conversation start, before new tasks, after completions
