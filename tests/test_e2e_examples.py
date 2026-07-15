"""End-to-end test: evaluate the example against its recorded JSON output.

Skipped when the `graphcal` binary is not on PATH.
"""
import json
import math
import shutil
import unittest
from pathlib import Path

import graphcal
from graphcal import Override

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = REPO_ROOT / "examples" / "orbital_transfer.gcl"
EXPECTED = REPO_ROOT / "examples" / "orbital_transfer.expected.json"

GRAPHCAL_BINARY = shutil.which("graphcal")


@unittest.skipUnless(GRAPHCAL_BINARY, "graphcal binary not found on PATH")
class OrbitalTransferExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = graphcal.eval(
            EXAMPLE,
            overrides=[
                Override.length("parking_orbit_altitude", 410.0, "km"),
                Override.angle("target_inclination", 51.6, "deg"),
            ],
            binary=GRAPHCAL_BINARY,
        )

    def test_raw_output_matches_expected_json(self):
        expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

        self.assertEqual(self.result.raw, expected)

    def test_delta_v_scales_to_km_per_s(self):
        delta_v = self.result.node("delta_v")

        self.assertAlmostEqual(delta_v.as_scaled(3), delta_v.si_value / 1_000.0)

    def test_orbital_radius_display_unit_is_km(self):
        orbital_radius = self.result.node("orbital_radius")

        self.assertEqual(orbital_radius.unit, "km")
        self.assertAlmostEqual(orbital_radius.display_value, 6788.137)

    def test_target_inclination_converts_to_degrees_caller_side(self):
        inclination = self.result.param("target_inclination")

        self.assertAlmostEqual(math.degrees(inclination.as_float()), 51.6)

    def test_check_passes_for_example(self):
        graphcal.check(EXAMPLE, binary=GRAPHCAL_BINARY)


if __name__ == "__main__":
    unittest.main()
