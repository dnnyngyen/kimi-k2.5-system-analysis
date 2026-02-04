# Tool Specification: mshtools-slides_generator

## Overview
PowerPoint (.pptx) generation tool converting HTML-formatted presentation source to native PPTX format. Uses specific CSS class structure for slide definition.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to save the .pptx.html source file"
    },
    "content": {
      "type": "string",
      "description": "HTML-formatted presentation source code"
    },
    "append": {
      "type": "boolean",
      "default": false,
      "description": "If true, append to existing file; if false, create new"
    }
  },
  "required": ["file_path", "content"]
}
```

## Streaming Mechanism
- **Processing Pipeline**:
  1. Validate HTML structure (must contain `ppt-slide` CSS class)
  2. Parse slide divs: `<div class="ppt-slide">...</div>`
  3. Convert to OpenXML PresentationML
  4. Generate .pptx file
  5. Push to user
- **Append Mode**: Allows incremental slide building across multiple calls

## Integration Architecture

### Conversion Engine
- **Input Format**: HTML + CSS with specific conventions
- **Output Format**: OOXML (.pptx) - Microsoft PowerPoint format
- **Slide Definition**: Each `<div class="ppt-slide">` = one slide

## HTML Requirements
```html
<div class="ppt-slide">
  <h1>Slide Title</h1>
  <p>Content here</p>
</div>
<div class="ppt-slide">
  <h1>Second Slide</h1>
  <ul>
    <li>Point 1</li>
    <li>Point 2</li>
  </ul>
</div>
```

## Usage Patterns

### Single Generation
```
slides_generator(
  file_path="/mnt/kimi/output/presentation.pptx.html",
  content='<div class="ppt-slide"><h1>Title</h1></div>'
)
```

### Incremental Building
```
# First batch
slides_generator(
  file_path="/mnt/kimi/output/pres.pptx.html",
  content='<div class="ppt-slide">...</div>',
  append=false
)

# Add more slides
slides_generator(
  file_path="/mnt/kimi/output/pres.pptx.html",
  content='<div class="ppt-slide">...</div>',
  append=true
)
```

## Workflow Integration
- **Design Phase**: Create visual design plan markdown
- **Outline Phase**: Create JSON outline
- **Generation Phase**: Use slides_generator for final output
