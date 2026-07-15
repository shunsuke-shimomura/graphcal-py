"""Typed accessors over the JSON produced by `graphcal eval --format json`."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


class GraphcalValue:
    """One value from a Graphcal result section.

    Wraps either a dimensioned dict (`{"si_value": ..., "display_value": ...,
    "unit": ...}`) or a plain scalar.
    """

    def __init__(self, raw: Any) -> None:
        self._raw = raw

    @property
    def raw(self) -> Any:
        return self._raw

    @property
    def unit(self) -> Optional[str]:
        if isinstance(self._raw, Mapping):
            return self._raw.get("unit")
        return None

    @property
    def si_value(self) -> Optional[float]:
        if isinstance(self._raw, Mapping):
            return self._raw.get("si_value")
        if isinstance(self._raw, (int, float)) and not isinstance(self._raw, bool):
            return self._raw
        return None

    @property
    def display_value(self) -> Optional[float]:
        if isinstance(self._raw, Mapping):
            return self._raw.get("display_value")
        if isinstance(self._raw, (int, float)) and not isinstance(self._raw, bool):
            return self._raw
        return None

    @property
    def value(self) -> Any:
        """The most useful plain value: SI when present, otherwise raw."""
        if isinstance(self._raw, Mapping):
            if "si_value" in self._raw:
                return self._raw["si_value"]
            return self._raw.get("display_value")
        return self._raw

    def as_float(self) -> float:
        """Return the value as `float`; raise `TypeError` when non-numeric."""
        candidate = self.si_value
        if candidate is None:
            raise TypeError(f"graphcal value is not numeric: {self._raw!r}")
        return float(candidate)

    def as_int(self) -> int:
        """Return the value as `int` (truncating), via `as_float`."""
        return int(self.as_float())

    def as_scaled(self, exponent: int) -> float:
        """Return the SI value divided by ``10 ** exponent``.

        Any real unit conversion (e.g. rad to deg) is the caller's
        responsibility; this only strips a decimal prefix, such as
        `as_scaled(3)` for m/s -> km/s.
        """
        return self.as_float() / 10.0 ** exponent

    def __repr__(self) -> str:
        return f"GraphcalValue({self._raw!r})"


class GraphcalResult:
    """Parsed output of `graphcal eval --format json`."""

    def __init__(self, raw: Mapping[str, Any]) -> None:
        self._raw = dict(raw)

    @property
    def raw(self) -> Dict[str, Any]:
        return self._raw

    def node(self, name: str) -> GraphcalValue:
        return self._lookup("node", name)

    def param(self, name: str) -> GraphcalValue:
        return self._lookup("param", name)

    def const(self, name: str) -> GraphcalValue:
        return self._lookup("const", name)

    def _lookup(self, section: str, name: str) -> GraphcalValue:
        entries = self._raw.get(section)
        if not isinstance(entries, Mapping) or name not in entries:
            raise KeyError(f"no {section!r} entry named {name!r} in result")
        return GraphcalValue(entries[name])

    def __repr__(self) -> str:
        sections = ", ".join(sorted(self._raw))
        return f"GraphcalResult(sections=[{sections}])"
