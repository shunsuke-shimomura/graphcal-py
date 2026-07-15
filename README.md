# graphcal-py

Python wrapper for the [graphcal](../graphcal) CLI. Wraps `graphcal eval
--format json` in a small typed API: result accessors, unit-aware override
builders, project discovery, and wrapped errors.

## Why subprocess, not PyO3

graphcal's Rust library API is not stable yet, so a PyO3 binding would break
too often. The CLI (`graphcal eval --format json`) is the more stable surface.
See [DESIGN.md](DESIGN.md).

## Install

```sh
# pip
pip install git+https://github.com/shunsuke-shimomura/graphcal-py.git

# uv (project)
uv add git+https://github.com/shunsuke-shimomura/graphcal-py.git
```

Requires `graphcal` on `PATH` (or pass `binary=...`).

## Use

```python
import graphcal

result = graphcal.eval(
    "examples/orbital_transfer.gcl",
    overrides=[
        graphcal.Override.length("parking_orbit_altitude", 410.0, "km"),
        graphcal.Override.angle("target_inclination", 51.6, "deg"),
        graphcal.Override.mass("propellant_mass", 2800.0, "kg"),
    ],
)

print(result.node("delta_v").as_scaled(3))          # 3.778... (m/s -> km/s)
print(result.node("orbital_radius").display_value)  # 6788.137 (km)
```

### Result accessors

`graphcal.eval` returns a `GraphcalResult`. Sections of the JSON output are
reachable through typed accessors that return `GraphcalValue`:

```python
result.node("delta_v").si_value          # SI value (m/s)
result.param("target_inclination").display_value  # value in its display unit
result.const("g0").unit                  # "m/s^2"
result.node("mass_ratio").as_float()     # plain float
result.node("delta_v").as_scaled(3)      # SI value / 10**3 (m/s -> km/s)
result.raw                               # untouched JSON dict
```

There is deliberately no unit-conversion table: `as_scaled(exponent)` only
strips a decimal prefix from the SI value. Real conversions (e.g. rad to
deg with `math.degrees`) belong to the caller; Graphcal itself remains
responsible for dimension checking.

### Overrides

Overrides can be a plain mapping or unit-aware builders that always format
parseable `--set` literals (`410.0 km`, never `410 km`):

```python
graphcal.Override.length("parking_orbit_altitude", 410.0, "km")
graphcal.Override.angle("target_inclination", 51.6, "deg")
graphcal.Override.scalar("mode_count", 9)
```

### Project discovery

Resolve `.gcl` files without depending on the current working directory:

```python
from graphcal import GraphcalProject

project = GraphcalProject.discover(start=__file__)  # walks up to graphcal.toml
result = project.eval("mission.transfer.orbital_insertion", overrides=...)
```

Dotted module names resolve under `<root>/<source_dir>/<package_name>/`;
relative `.gcl` paths resolve from the project root.

### Errors

CLI failures raise `GraphcalEvaluationError` (for `eval`) or
`GraphcalCheckError` (for `check`) instead of a bare
`subprocess.CalledProcessError`. Both keep `command`, `stdout`, `stderr`, and
`returncode`; evaluation errors also keep `file` and the normalized
`overrides`.

## Development

```sh
PYTHONPATH=src python -m unittest discover -v
graphcal check examples/orbital_transfer.gcl
```

The E2E test in `tests/test_e2e_examples.py` runs only when `graphcal` is on
`PATH` and compares the example against
`examples/orbital_transfer.expected.json`.
