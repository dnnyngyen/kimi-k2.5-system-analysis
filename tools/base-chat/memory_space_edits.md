# Tool Specification: memory_space_edits

## Overview
Long-term memory management for persisting information across conversations. Add, replace, or remove memories that persist beyond current session.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "operate": {
      "type": "string",
      "enum": ["add", "remove", "replace"],
      "description": "Operation type"
    },
    "content": {
      "type": "string",
      "description": "Memory content (required for add/replace)"
    },
    "id": {
      "type": "string",
      "description": "Memory ID (required for remove/replace)"
    }
  },
  "required": ["operate"]
}
```

## Streaming Mechanism
- **Storage**: Persistent database (survives conversation restart)
- **Operations**:
  - `add`: Create new memory entry
  - `replace`: Update existing by ID
  - `remove`: Delete by ID
- **Return**: Confirmation of operation

## Memory Structure
```json
{
  "id": "3",
  "date": "26-01-28",
  "content": "User preference for technical discussions"
}
```

## Content Rules
- **Start with**: "User" or user name (e.g., "User works as...")
- **Language**: Same as conversation language
- **Forbidden**: Sensitive data (race, religion, health, minors <18, precise location)

## Integration Architecture
- **Scope**: Cross-conversation persistence
- **Loading**: Memories injected into context at conversation start
- **Display**: Shown in system prompt under "Memory" section
- **Privacy**: User-controlled, can disable in Settings

## Usage Patterns

### Add Memory
```
memory_space_edits(
  operate="add",
  content="User prefers Python for data analysis"
)
```

### Update Memory
```
memory_space_edits(
  operate="replace",
  id="3",
  content="User prefers Rust for systems programming"
)
```

### Delete Memory
```
memory_space_edits(operate="remove", id="3")
```

## System Integration
- **Available in**: Both Base Chat and OK Computer
- **User Control**: Can disable via Settings → Personalization → Memory space
- **Transparency**: User shown all stored memories
