"""Graphcal project discovery and module path resolution."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

from .cli import DEFAULT_BINARY, eval_file
from .errors import GraphcalError
from .overrides import OverrideInput
from .result import GraphcalResult

MANIFEST_NAME = "graphcal.toml"
DEFAULT_SOURCE_DIR = "src"


@dataclass(frozen=True)
class GraphcalProject:
    """A Graphcal package rooted at a `graphcal.toml` manifest."""

    root: Path
    package_name: str
    source_dir: Path = Path(DEFAULT_SOURCE_DIR)

    @classmethod
    def discover(cls, start: Union[str, Path]) -> "GraphcalProject":
        """Walk upward from *start* until a `graphcal.toml` is found."""
        origin = Path(start).resolve()
        candidates = [origin] if origin.is_dir() else []
        candidates += list(origin.parents)
        for directory in candidates:
            manifest = directory / MANIFEST_NAME
            if manifest.is_file():
                package_name, source_dir = _read_manifest(manifest)
                return cls(
                    root=directory,
                    package_name=package_name or directory.name,
                    source_dir=Path(source_dir or DEFAULT_SOURCE_DIR),
                )
        raise GraphcalError(f"no {MANIFEST_NAME} found walking up from {origin}")

    def file(self, module: Union[str, Path]) -> Path:
        """Resolve a dotted module name or a `.gcl` path to an absolute path.

        Direct `.gcl` paths (and anything containing a path separator) are
        resolved from the project root. Dotted module names resolve under
        `root / source_dir / package_name`; a leading segment equal to the
        package name is dropped.
        """
        if isinstance(module, Path):
            return module if module.is_absolute() else self.root / module
        if module.endswith(".gcl") or "/" in module or "\\" in module:
            path = Path(module)
            return path if path.is_absolute() else self.root / path
        segments = module.split(".")
        if segments[0] == self.package_name:
            segments = segments[1:]
        if not segments:
            raise GraphcalError(f"module name resolves to no file: {module!r}")
        relative = Path(*segments[:-1]) / f"{segments[-1]}.gcl"
        return self.root / self.source_dir / self.package_name / relative

    def eval(
        self,
        module: Union[str, Path],
        *,
        overrides: OverrideInput = None,
        binary: str = DEFAULT_BINARY,
    ) -> GraphcalResult:
        """Evaluate a module of this project via `eval_file`."""
        return eval_file(self.file(module), overrides=overrides, binary=binary)


def _read_manifest(manifest: Path) -> Tuple[Optional[str], Optional[str]]:
    """Read `[package] name` and `source_dir` (with root-level fallback)."""
    text = manifest.read_text(encoding="utf-8")
    try:
        import tomllib
    except ModuleNotFoundError:  # Python < 3.11
        return _parse_manifest_fallback(text)
    data = tomllib.loads(text)
    package = data.get("package", {})
    name = package.get("name")
    source_dir = package.get("source_dir") or data.get("source_dir")
    return name, source_dir


def _parse_manifest_fallback(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Line-based fallback parser for the two manifest keys we need."""
    name: Optional[str] = None
    package_source_dir: Optional[str] = None
    root_source_dir: Optional[str] = None
    section = ""
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if section == "package" and key == "name":
            name = value
        elif section == "package" and key == "source_dir":
            package_source_dir = value
        elif section == "" and key == "source_dir":
            root_source_dir = value
    return name, package_source_dir or root_source_dir
