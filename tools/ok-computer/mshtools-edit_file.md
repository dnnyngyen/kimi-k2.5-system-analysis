# Tool Specification: mshtools-edit_file

## Overview
String replacement tool for modifying existing files. Performs exact string matching with support for multi-line replacements and replace-all mode.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Absolute path to file"
    },
    "old_string": {
      "type": "string",
      "description": "Exact text to find and replace (must be unique unless replace_all=true)"
    },
    "new_string": {
      "type": "string",
      "description": "Replacement text"
    },
    "replace_all": {
      "type": "boolean",
      "default": false,
      "description": "Replace all occurrences instead of just first"
    }
  },
  "required": ["file_path", "old_string", "new_string"]
}
```

## Streaming Mechanism
- **Edit Algorithm**:
  1. Read file content
  2. Locate old_string (must be unique unless replace_all)
  3. Replace with new_string
  4. Write back to file
  5. Return success confirmation
- **Uniqueness Check**: Fails if old_string appears multiple times and replace_all=false
- **Indentation**: Preserves exact whitespace (tabs/spaces) from old_string

## Integration Architecture

### Safety Requirements
- **MUST read_file first**: Tool will error if attempting edit without prior read
- **Unique Matching**: old_string must be unique in file (or use replace_all)
- **Line Number Context**: read_file output includes line numbers but they must NOT be included in old_string

## Usage Patterns

### Single Replacement
```python
# First: read the file
read_file(file_path="/path/to/file.txt")
# Returns line-numbered content

# Then: edit (note: no line numbers in strings)
edit_file(
  file_path="/path/to/file.txt",
  old_string="  old_function()",
  new_string="  new_function()"
)
```

### Multi-Line Replacement
```python
edit_file(
  file_path="/path/to/config.json",
  old_string='''{
  "setting": "old_value",
  "enabled": true
}''',
  new_string='''{
  "setting": "new_value",
  "enabled": false
}'''
)
```

### Rename Variable (Replace All)
```python
edit_file(
  file_path="/path/to/code.py",
  old_string="old_var_name",
  new_string="new_var_name",
  replace_all=true
)
```

## Error Handling
- **Not Unique**: Error if old_string appears multiple times (without replace_all)
- **Not Found**: Error if old_string doesn't exist in file
- **No Read First**: Error if file wasn't read in this conversation
- **Identical Strings**: Error if old_string == new_string
