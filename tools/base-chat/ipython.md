# Tool Specification: ipython (Base Chat)

## Overview
Python execution environment for Base Chat. Same core functionality as OK Computer but with different constraints.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "description": "Python code to execute"
    },
    "restart": {
      "type": "boolean",
      "default": false,
      "description": "Restart kernel (clears all state)"
    }
  },
  "required": ["code"]
}
```

## Architectural Position

IPython is the **primary computation engine** providing stateful execution with memory persistence across calls. Unlike shell's fresh sessions, IPython maintains variable state.

## Kernel Architecture

### Process Model
```
Kernel Server (FastAPI :8888)
    ↓
Jupyter Kernel (ZeroMQ)
    ↓
IPython Kernel (PID 300+)
    ↓
Execution Namespace (persistent)
```

### Communication Flow
1. Tool invocation with code string
2. FastAPI routing via kernel_server.py
3. ZMQ dispatch to IPython kernel
4. Code execution
5. Result capture (stdout, display, errors)
6. JSON response to model

## State Persistence

### What Persists
- Global variables
- Imported modules
- Function/class definitions
- matplotlib configuration

### What Does Not Persist
- File descriptors (auto-closed)
- Network connections
- Subprocess objects

### Reset Mechanism
restart=True clears everything. Kernel reset endpoint: POST :8888/kernel/reset

## Library Ecosystem

### Pre-installed Stack
- pandas (data manipulation)
- numpy (numerical computing)
- torch 2.8.0 (PyTorch, CPU only)
- matplotlib (visualization)
- Pillow (image processing)
- OpenCV (computer vision)
- sqlite3 (database)

## Skill-Specific Patterns

### DOCX: Meta-Programming
Python generates C# code that generates documents:
```python
cs_template = f'using DocumentFormat.OpenXml...'
with open('/tmp/Program.cs', 'w') as f:
    f.write(cs_template)
```

### XLSX: Direct Manipulation
Direct Excel manipulation via openpyxl:
```python
from openpyxl import Workbook
wb = Workbook()
ws['A1'] = '=SUM(B:B)'  # Formula injection
wb.save('output.xlsx')
```

### PDF: Source Generation
Generate markup for external renderer:
```python
html = f'<html>...{content}...</html>'
with open('/tmp/input.html', 'w') as f:
    f.write(html)
```

### WebApp: Code Generation
Generate TypeScript for external build:
```python
component = f'export function...'
# Written via write_file tool
```

## Data Processing

### Pandas Workflow
```python
import pandas as pd
df = pd.read_csv('data.csv')
summary = df.groupby('category').sum()
summary.to_csv('output.csv')
```

### NumPy Computation
```python
import numpy as np
arr = np.random.randn(1000000)
mean = np.mean(arr)
```

## Visualization

### Matplotlib Integration
Automatic display without plt.show():
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(x, y)  # Auto-displayed
```

## Image Processing

### Pillow
```python
from PIL import Image
img = Image.open('photo.jpg')
img = img.resize((800, 600))
img.save('output.png')
```

### OpenCV
```python
import cv2
img = cv2.imread('photo.jpg')
edges = cv2.Canny(img, 100, 200)
```

## Constraints

### Hard Limits
- Network access blocked
- 4GB RAM limit
- 30s execution timeout
- No persistent storage outside output dirs

### Package Installation
pip install works but packages lost on kernel restart.

## Summary

IPython is the **cognitive engine**:
- Direct manipulation (openpyxl, lxml)
- Code generation (C#, LaTeX, HTML, TSX)
- Data processing (pandas, numpy)
- Visualization (matplotlib)
- Image processing (Pillow, OpenCV)

Stateful execution enables multi-turn workflows.

## Differences from OK Computer
| Aspect | Base Chat | OK Computer |
|--------|-----------|-------------|
| Paths | /mnt/kimi/upload (RO), /mnt/kimi/output (RW) | /mnt/okcomputer/* |
| Step Budget | 10 per turn | 200-300 per session |
| Context | No skill files | Skill files available |
| Todo List | No | Yes |
| Browser Tools | No (web_open_url only) | Full Playwright suite |

## Usage
Identical to OK Computer mshtools-ipython:
```
ipython(code="print('Hello')")
```

## System Integration
- **Kernel**: Same jupyter_kernel.py backend
- **Control**: kernel_server.py:8888
- **Libraries**: Same pre-installed packages (PyTorch, pandas, etc.)
- **Network**: Same restrictions (blocked)
