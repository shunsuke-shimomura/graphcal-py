"""Tests for GraphcalResult / GraphcalValue accessors."""
import unittest

from graphcal import GraphcalResult

SAMPLE = {
    "const": {
        "g0": {"display_value": 9.80665, "si_value": 9.80665, "unit": "m/s^2"},
    },
    "node": {
        "delta_v": {"si_value": 3778.22, "unit": "m/s"},
        "orbital_radius": {
            "display_value": 6788.137,
            "si_value": 6788137.0,
            "unit": "km",
        },
        "mass_ratio": {"si_value": 3.3333333},
    },
    "param": {
        "target_inclination": {
            "display_value": 51.6,
            "si_value": 0.9005898940290741,
            "unit": "deg",
        },
        "mode_count": 9,
    },
}


class SectionAccessorTest(unittest.TestCase):
    def setUp(self):
        self.result = GraphcalResult(SAMPLE)

    def test_node_param_and_const_accessors_return_values(self):
        self.assertEqual(self.result.node("delta_v").si_value, 3778.22)
        self.assertEqual(self.result.param("target_inclination").display_value, 51.6)
        self.assertEqual(self.result.const("g0").unit, "m/s^2")

    def test_missing_name_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.result.node("does_not_exist")

    def test_raw_returns_full_json(self):
        self.assertEqual(self.result.raw, SAMPLE)


class ValueBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.result = GraphcalResult(SAMPLE)

    def test_value_prefers_si_value_for_dict_values(self):
        self.assertEqual(
            self.result.param("target_inclination").value, 0.9005898940290741
        )

    def test_plain_numeric_value_exposes_number_everywhere(self):
        value = self.result.param("mode_count")

        self.assertEqual(value.value, 9)
        self.assertEqual(value.si_value, 9)
        self.assertEqual(value.display_value, 9)
        self.assertIsNone(value.unit)

    def test_as_float_and_as_int(self):
        self.assertAlmostEqual(self.result.node("mass_ratio").as_float(), 3.3333333)
        self.assertEqual(self.result.param("mode_count").as_int(), 9)

    def test_as_float_raises_type_error_for_non_numeric(self):
        result = GraphcalResult({"node": {"label": "not a number"}})

        with self.assertRaises(TypeError):
            result.node("label").as_float()


class AsScaledTest(unittest.TestCase):
    def setUp(self):
        self.result = GraphcalResult(SAMPLE)

    def test_positive_exponent_strips_decimal_prefix(self):
        self.assertAlmostEqual(self.result.node("delta_v").as_scaled(3), 3.77822)
        self.assertAlmostEqual(
            self.result.node("orbital_radius").as_scaled(3), 6788.137
        )

    def test_zero_exponent_returns_si_value(self):
        self.assertEqual(self.result.node("delta_v").as_scaled(0), 3778.22)

    def test_negative_exponent_scales_up(self):
        self.assertAlmostEqual(self.result.node("delta_v").as_scaled(-3), 3778220.0)

    def test_scaling_non_numeric_raises_type_error(self):
        result = GraphcalResult({"node": {"label": "text"}})

        with self.assertRaises(TypeError):
            result.node("label").as_scaled(3)


if __name__ == "__main__":
    unittest.main()
