"""Subprocess wrappers around the `graphcal` CLI.

The Rust library API is not the integration surface; this module shells
out to `graphcal eval --format json` and `graphcal check`.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Union

from .errors import GraphcalCheckError, GraphcalError, GraphcalEvaluationError
from .overrides import OverrideInput, normalize_overrides
from .result import GraphcalResult

DEFAULT_BINARY = "graphcal"


def eval_file(
    file: Union[str, Path],
    *,
    overrides: OverrideInput = None,
    binary: str = DEFAULT_BINARY,
) -> GraphcalResult:
    """Run `graphcal eval --format json` on *file* and return the result.

    Raises `GraphcalEvaluationError` on non-zero exit (compile, runtime,
    or assertion failures).
    """
    target = Path(file)
    normalized = normalize_overrides(overrides)
    cmd = [binary, "eval", "--format", "json", str(target)]
    for name, value in normalized.items():
        cmd += ["--set", f"{name}={value}"]
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise GraphcalEvaluationError(
            command=cmd,
            stdout=exc.stdout,
            stderr=exc.stderr,
            returncode=exc.returncode,
            file=target,
            overrides=normalized,
        ) from exc
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise GraphcalError(
            f"graphcal eval produced invalid JSON for {target}: {exc}"
        ) from exc
    return GraphcalResult(parsed)


def eval(  # noqa: A001 - public API name, kept for compatibility
    file: Union[str, Path],
    *,
    overrides: OverrideInput = None,
    binary: str = DEFAULT_BINARY,
) -> GraphcalResult:
    """Public alias for `eval_file` (kept as `graphcal.eval`)."""
    return eval_file(file, overrides=overrides, binary=binary)


def check(
    target: Union[str, Path],
    *,
    binary: str = DEFAULT_BINARY,
) -> None:
    """Run `graphcal check` on *target* (a file or directory).

    Raises `GraphcalCheckError` when errors are detected.
    """
    cmd = [binary, "check", str(target)]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise GraphcalCheckError(
            command=cmd,
            stdout=exc.stdout,
            stderr=exc.stderr,
            returncode=exc.returncode,
        ) from exc
