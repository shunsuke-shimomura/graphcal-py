"""Unit-aware `--set` override builders."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Dict, Union

OverrideValue = Union[str, int, float]
OverrideInput = Union[
    Mapping[str, OverrideValue],
    Iterable["Override"],
    None,
]


@dataclass(frozen=True)
class Override:
    """A single `--set name=value` override for `graphcal eval`."""

    name: str
    value: str

    @classmethod
    def quantity(cls, name: str, value: float, unit: str) -> "Override":
        """Build a unitful override such as `410.0 km`.

        The number is always formatted as a float because `--set` requires
        parseable literals (`45.0 deg`, not `45 deg`).
        """
        return cls(name, f"{float(value)} {unit}")

    @classmethod
    def scalar(cls, name: str, value: OverrideValue) -> "Override":
        """Build a dimensionless override (plain number)."""
        return cls(name, str(value))

    @classmethod
    def length(cls, name: str, value: float, unit: str = "m") -> "Override":
        return cls.quantity(name, value, unit)

    @classmethod
    def area(cls, name: str, value: float, unit: str = "m^2") -> "Override":
        return cls.quantity(name, value, unit)

    @classmethod
    def mass(cls, name: str, value: float, unit: str = "kg") -> "Override":
        return cls.quantity(name, value, unit)

    @classmethod
    def time(cls, name: str, value: float, unit: str = "s") -> "Override":
        return cls.quantity(name, value, unit)

    @classmethod
    def frequency(cls, name: str, value: float, unit: str = "Hz") -> "Override":
        return cls.quantity(name, value, unit)

    @classmethod
    def angle(cls, name: str, value: float, unit: str = "deg") -> "Override":
        return cls.quantity(name, value, unit)

    @classmethod
    def power(cls, name: str, value: float, unit: str = "W") -> "Override":
        return cls.quantity(name, value, unit)

    @classmethod
    def velocity(cls, name: str, value: float, unit: str = "m/s") -> "Override":
        return cls.quantity(name, value, unit)


def normalize_overrides(overrides: OverrideInput) -> Dict[str, str]:
    """Normalize a mapping or an iterable of `Override` to `{name: value}`.

    Mapping values are stringified; `Override` instances are used as-is.
    """
    if overrides is None:
        return {}
    if isinstance(overrides, Mapping):
        return {str(name): str(value) for name, value in overrides.items()}
    normalized: Dict[str, str] = {}
    for item in overrides:
        if not isinstance(item, Override):
            raise TypeError(
                "overrides iterable must contain Override instances, "
                f"got {type(item).__name__}"
            )
        normalized[item.name] = item.value
    return normalized
