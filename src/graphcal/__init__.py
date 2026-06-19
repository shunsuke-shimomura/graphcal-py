"""Minimal subprocess wrapper for the graphcal CLI."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def eval(
    file: str | Path,
    *,
    overrides: dict[str, str] | None = None,
    binary: str = "graphcal",
) -> dict[str, Any]:
    """Run `graphcal eval --format json` on *file* and return parsed JSON.

    Raises `subprocess.CalledProcessError` on non-zero exit (compile / runtime /
    assertion failures). stderr is attached to the exception.
    """
    cmd = [binary, "eval", "--format", "json", str(file)]
    for k, v in (overrides or {}).items():
        cmd += ["--set", f"{k}={v}"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)
