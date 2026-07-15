"""Exception hierarchy for graphcal CLI failures."""
from __future__ import annotations

from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple


class GraphcalError(Exception):
    """Base class for all graphcal-py errors."""


class GraphcalCommandError(GraphcalError):
    """A `graphcal` subprocess exited with a non-zero status."""

    def __init__(
        self,
        message: str,
        *,
        command: Sequence[str],
        stdout: Optional[str],
        stderr: Optional[str],
        returncode: int,
    ) -> None:
        super().__init__(message)
        self.command: Tuple[str, ...] = tuple(command)
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class GraphcalEvaluationError(GraphcalCommandError):
    """`graphcal eval` failed (compile error, runtime error, or assertion)."""

    def __init__(
        self,
        *,
        command: Sequence[str],
        stdout: Optional[str],
        stderr: Optional[str],
        returncode: int,
        file: Path,
        overrides: Mapping[str, str],
    ) -> None:
        message = f"graphcal eval failed for {file} (exit code {returncode})"
        if stderr:
            message = f"{message}\n{stderr.strip()}"
        super().__init__(
            message,
            command=command,
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
        )
        self.file = Path(file)
        self.overrides = dict(overrides)


class GraphcalCheckError(GraphcalCommandError):
    """`graphcal check` reported errors."""

    def __init__(
        self,
        *,
        command: Sequence[str],
        stdout: Optional[str],
        stderr: Optional[str],
        returncode: int,
    ) -> None:
        message = f"graphcal check failed (exit code {returncode})"
        if stderr:
            message = f"{message}\n{stderr.strip()}"
        super().__init__(
            message,
            command=command,
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
        )
