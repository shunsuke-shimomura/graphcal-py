"""Tests for GraphcalResult / GraphcalValue accessors."""
import pytest

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


@pytest.fixture
def result():
    return GraphcalResult(SAMPLE)


class TestSectionAccessors:
    def test_node_param_and_const_accessors_return_values(self, result):
        assert result.node("delta_v").si_value == 3778.22
        assert result.param("target_inclination").display_value == 51.6
        assert result.const("g0").unit == "m/s^2"

    def test_missing_name_raises_key_error(self, result):
        with pytest.raises(KeyError):
            result.node("does_not_exist")

    def test_raw_returns_full_json(self, result):
        assert result.raw == SAMPLE


class TestValueBehavior:
    def test_value_prefers_si_value_for_dict_values(self, result):
        assert result.param("target_inclination").value == 0.9005898940290741

    def test_plain_numeric_value_exposes_number_everywhere(self, result):
        value = result.param("mode_count")

        assert value.value == 9
        assert value.si_value == 9
        assert value.display_value == 9
        assert value.unit is None

    def test_as_float_and_as_int(self, result):
        assert result.node("mass_ratio").as_float() == pytest.approx(3.3333333)
        assert result.param("mode_count").as_int() == 9

    def test_as_float_raises_type_error_for_non_numeric(self):
        result = GraphcalResult({"node": {"label": "not a number"}})

        with pytest.raises(TypeError):
            result.node("label").as_float()


class TestAsScaled:
    def test_positive_exponent_strips_decimal_prefix(self, result):
        assert result.node("delta_v").as_scaled(3) == pytest.approx(3.77822)
        assert result.node("orbital_radius").as_scaled(3) == pytest.approx(6788.137)

    def test_zero_exponent_returns_si_value(self, result):
        assert result.node("delta_v").as_scaled(0) == 3778.22

    def test_negative_exponent_scales_up(self, result):
        assert result.node("delta_v").as_scaled(-3) == pytest.approx(3778220.0)

    def test_scaling_non_numeric_raises_type_error(self):
        result = GraphcalResult({"node": {"label": "text"}})

        with pytest.raises(TypeError):
            result.node("label").as_scaled(3)
