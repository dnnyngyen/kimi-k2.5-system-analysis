# Utility Functions

The utils.py module provides common utility functions for the Kimi agent system. At just 41 lines, this lightweight module contains helper functions for display detection, subprocess execution, and system operations.

---

## Display Detection

The `get_screensize()` function detects the X11 display resolution using xrandr.

```python
def get_screensize() -> Tuple[int, int]:
    """Get screen resolution using xrandr"""
    result = subprocess.run(
        ["xrandr | grep -oP '(?<=current )\\d+ x \\d+' | tr -d ' '"],
        shell=True, capture_output=True, text=True
    )

    if result.returncode == 0:
        match = re.match(r'(\d+)x(\d+)', result.stdout.strip())
        if match:
            return int(match.group(1)), int(match.group(2))

    # Fallback to default
    return 1920, 1080
```

This function parses the output of xrandr to extract the current screen resolution. If parsing fails, it falls back to a standard 1920x1080 resolution. The function returns a tuple of (width, height) in pixels.

---

## Synchronous Subprocess Execution

The `run_command()` function executes subprocesses with timeout handling.

```python
def run_command(
    command: List[str],
    timeout: int = 30,
    pipe_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a command with timeout and output capture"""
    return subprocess.run(
        command,
        capture_output=pipe_output,
        text=True,
        timeout=timeout
    )
```

This is used throughout the system for running external tools. The timeout prevents hung processes from blocking indefinitely. Output capture allows the caller to inspect stdout and stderr.

---

## Background Process Spawning

The `run_command_background()` function spawns asynchronous processes for background tasks.

```python
def run_command_background(command: List[str]) -> subprocess.Popen:
    """Run a command in the background"""
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
```

This returns a Popen object that the caller can monitor or terminate as needed. It's used for long-running processes that shouldn't block the main execution flow.

---

## Dependencies

The module uses only standard library imports:

- `subprocess` — Process execution
- `re` — Regex parsing for display resolution
- `typing` — Type hints for function signatures

This minimal dependency set makes the module reliable and portable across Python environments.

---

## Usage Patterns

Display detection is used by browser_guard.py to determine viewport size for screenshots. Subprocess execution is used throughout the system for running shell commands, compilers, and validation tools. Background spawning is used for starting long-running services.

The module is intentionally simple. Complex functionality belongs in specialized modules; utils.py provides the basic building blocks that multiple components need.
