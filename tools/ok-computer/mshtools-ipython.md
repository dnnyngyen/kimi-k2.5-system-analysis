# Tool Specification: mshtools-ipython

## Overview
Interactive Python execution environment providing Jupyter Notebook-style computation, data analysis, and visualization capabilities. Supports matplotlib charts, Pillow/OpenCV image processing, and persistent variable state across executions.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "description": "Python code to run in the IPython environment"
    },
    "restart": {
      "type": "boolean",
      "default": false,
      "description": "Whether to restart the IPython environment (resets all variables and imports)"
    }
  },
  "required": ["code"]
}
```

## Streaming Mechanism
- **Transport**: WebSocket-like persistent connection to Jupyter kernel
- **Execution Model**: REPL (Read-Eval-Print Loop) with state persistence
- **Output Streams**: 
  - STDOUT/STDERR text output
  - Display output (matplotlib figures auto-rendered)
  - Error tracebacks with full exception details
- **State Persistence**: Variables and imports persist across executions within same session
- **Kernel Management**: Control plane manages kernel lifecycle via FastAPI (port 8888)

## Integration Architecture

### Container Infrastructure
```
Layer 1: Control Plane (kernel_server.py:8888) - FastAPI lifecycle management
    ↓
Layer 2: Compute Engine (jupyter_kernel.py) - IPython kernel via ZeroMQ
    ↓
Layer 3: Execution Environment - Python 3.x with PyTorch 2.8.0, CUDA 12.8
```

### Execution Flow
1. **Code Submission**: Model sends code block via tool invocation
2. **Kernel Routing**: Control plane routes to active IPython kernel (PID 300-400)
3. **Execution**: ZeroMQ sockets execute code in sandboxed environment
4. **Result Capture**: Output captured from stdio and display hooks
5. **State Update**: Global namespace updated with new variables
6. **Response Streaming**: Results returned with text/image data

### External Dependencies
- **Pre-installed Packages**: PyTorch 2.8.0, NumPy, pandas, matplotlib, Pillow, OpenCV, SQLite
- **Network Access**: BLOCKED (containerized - no outbound requests)
- **File System**: 
  - `/mnt/kimi/upload` (read-only user files)
  - `/mnt/kimi/output` (write deliverables)
  - `/dev/shm` (shared memory for inter-process)

### Resource Constraints
- **Memory**: 4GB RAM (CPU-only)
- **Storage**: 0MB free (containerized, volatile)
- **Timeout**: 30s execution timeout per call
- **Step Budget**: Counts as 1 tool call against 10-step (Base) or 200-300 step (OK Computer) limit

## Special Capabilities

### Image Processing
- **Matplotlib**: Automatic figure display (no plt.show() needed)
- **Pillow**: Image loading, processing, filtering, format conversion
- **OpenCV**: Edge detection, color space conversion, morphological operations

### Shell Integration
- **Bang Commands**: `!ls -la`, `!pip install` (though packages don't persist across restarts)
- **Bash Chaining**: Combine multiple shell commands with `&&`, `;`, `||`

### Data Analysis
- **pandas**: DataFrame processing, CSV/Excel I/O
- **PyTorch**: Tensor operations, model inference (no training - no GPU persistence)
- **SQLite**: In-memory and file-based database operations

## Usage Patterns

### When to Use
- Numerical computation and mathematical operations
- Data processing of user-uploaded files (CSV/Excel/JSON)
- Chart generation (matplotlib)
- Image manipulation
- Complex logic requiring iterative computation

### Restrictions
- **Network Blocked**: urllib, requests, wget will fail
- **No Package Persistence**: pip install works but resets on kernel restart
- **File Size Limits**: Text >10000 chars truncated, images auto-compressed
