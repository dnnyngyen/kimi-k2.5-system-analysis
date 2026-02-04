import subprocess
from typing import Tuple, List


def get_screensize() -> Tuple[int, int]:
    """Get the screen size of the primary display."""
    display_size = (
        subprocess.run(
            "xrandr | grep -oP '(?<=current )\d+ x \d+' | tr -d ' '",  # pyright: ignore[reportInvalidStringEscapeSequence]
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        .stdout.decode()
        .strip()
    )
    return tuple(map(int, display_size.split("x")))  # type: ignore


def run_command(
    command: List[str], timeout: int = 30, pipe_output: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a shell command and return the output, error and exit code."""
    result = subprocess.run(
        command,
        text=True,
        timeout=timeout,
        stdout=subprocess.PIPE if pipe_output else None,
        stderr=subprocess.PIPE if pipe_output else None,
    )
    return result


def run_command_background(command: List[str]) -> subprocess.Popen:
    """Run a shell command in the background and return the process object."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return process
