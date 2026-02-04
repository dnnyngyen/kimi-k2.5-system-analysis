# Tool Specification: mshtools-read_file

## Overview
Universal file reader supporting text, images, video, and complex binary files (converting Office/PDF to markdown). Provides direct filesystem access for content ingestion and analysis.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Absolute path to file (must be absolute, not relative)"
    },
    "offset": {
      "type": "integer",
      "description": "Line offset for partial reading (optional, default: 0)"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum lines to read (optional, default: 1000)"
    }
  },
  "required": ["file_path"]
}
```

## Streaming Mechanism
- **Transport**: Direct filesystem read via kernel
- **Processing Pipeline**:
  - Text files: Line-numbered output (cat -n format)
  - Images: Direct pixel data display in chat interface
  - Videos: Metadata extraction + frame preview (for MP4, MOV, WEBM, MKV, AVI, M4V ≤100MB)
  - Binary files (Office/PDF ≤20MB): Conversion to markdown via parsing engines
- **Truncation**: Lines >2000 characters truncated; Text files >100MB rejected
- **Output Format**: Contextual based on MIME type detection

## Integration Architecture

### File Type Handlers
| Type | Extension | Handler | Output Format |
|------|-----------|---------|---------------|
| Text | .txt, .md, .py, etc | Direct read | Line-numbered text |
| Image | .png, .jpg, etc | Native display | Inline image |
| Video | .mp4, .mov, etc | FFmpeg metadata | Metadata + thumbnail |
| Word | .docx | OpenXML parser | Markdown |
| Excel | .xlsx | OpenXML parser | Markdown table |
| PDF | .pdf | pdfplumber/pikepdf | Markdown |
| Archive | .zip, .tar | Listing | File tree |

### Path Resolution
- **Absolute Required**: Must start with `/` (e.g., `/mnt/kimi/upload/file.txt`)
- **Automatic Expansion**: `~` not supported (use explicit paths)
- **Symlink Resolution**: Followed automatically
- **Access Control**: Respects filesystem permissions

### Performance Characteristics
- **Large Files**: Partial reading supported via offset/limit
- **Binary Conversion**: CPU-intensive for Office/PDF (runs in isolated process)
- **Image Loading**: Direct memory mapping for fast display
- **Caching**: No caching; re-reads file on each call

## Usage Patterns

### Sequential Reading
```
Step 1: read_file(/path/to/large.txt, offset=0, limit=1000)   # Lines 1-1000
Step 2: read_file(/path/to/large.txt, offset=1000, limit=1000) # Lines 1001-2000
```

### Image Analysis
```
read_file(/mnt/kimi/upload/chart.png)  # Displays image for vision analysis
```

### Document Ingestion
```
read_file(/mnt/kimi/upload/report.docx)  # Converts to markdown for text analysis
```

## Error Handling
- **Non-existent**: Returns error with "file not found"
- **Permission Denied**: Returns error if read access blocked
- **Size Exceeded**: Returns error for files exceeding limits
- **Malformed Binary**: Best-effort parsing with partial content warnings

## Skill Integration
- **docx skill**: Reads SKILL.md, C# templates, validation schemas
- **xlsx skill**: Reads Excel files for data analysis
- **pdf skill**: Reads existing PDFs for processing route
- **webapp skill**: Reads source code files during development
