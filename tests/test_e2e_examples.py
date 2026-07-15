"""End-to-end test: evaluate the example against its recorded JSON output.

Skipped when the `graphcal` binary is not on PATH.
"""
import json
import math
import shutil
from pathlib import Path

import pytest

import graphcal
from graphcal import Override

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = REPO_ROOT / "examples" / "orbital_transfer.gcl"
EXPECTED = REPO_ROOT / "examples" / "orbital_transfer.expected.json"

GRAPHCAL_BINARY = shutil.which("graphcal")

pytestmark = pytest.mark.skipif(
    GRAPHCAL_BINARY is None, reason="graphcal binary not found on PATH"
)


@pytest.fixture(scope="module")
def result():
    return graphcal.eval(
        EXAMPLE,
        overrides=[
            Override.length("parking_orbit_altitude", 410.0, "km"),
            Override.angle("target_inclination", 51.6, "deg"),
        ],
        binary=GRAPHCAL_BINARY,
    )


def test_raw_output_matches_expected_json(result):
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

    assert result.raw == expected


def test_delta_v_scales_to_km_per_s(result):
    delta_v = result.node("delta_v")

    assert delta_v.as_scaled(3) == pytest.approx(delta_v.si_value / 1_000.0)


def test_orbital_radius_display_unit_is_km(result):
    orbital_radius = result.node("orbital_radius")

    assert orbital_radius.unit == "km"
    assert orbital_radius.display_value == pytest.approx(6788.137)


def test_target_inclination_converts_to_degrees_caller_side(result):
    inclination = result.param("target_inclination")

    assert math.degrees(inclination.as_float()) == pytest.approx(51.6)


def test_check_passes_for_example():
    graphcal.check(EXAMPLE, binary=GRAPHCAL_BINARY)
