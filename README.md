# graphcal-py

Minimal Python wrapper for the [graphcal](../graphcal) CLI. PoC stage.

## Why subprocess, not PyO3

graphcal's Rust library API is not stable yet, so a PyO3 binding would break too often. The CLI (`graphcal eval --format json`) is the more stable surface. See [DESIGN.md](DESIGN.md).

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

result = graphcal.eval("rocket.gcl", overrides={"isp": "450.0 s"})
print(result["node"]["delta_v"]["si_value"])
```
