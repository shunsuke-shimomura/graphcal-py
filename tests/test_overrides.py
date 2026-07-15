"""Tests for the unit-aware override builders."""
import pytest

from graphcal import Override, normalize_overrides


class TestQuantityOverride:
    def test_quantity_formats_parseable_set_value(self):
        override = Override.quantity("isp", 320, "s")

        assert override.value == "320.0 s"

    def test_length_defaults_to_meters(self):
        override = Override.length("target_range", 700000.0)

        assert override.value == "700000.0 m"

    def test_angle_formats_float_degrees(self):
        override = Override.angle("target_inclination", 51.6, "deg")

        assert override == Override("target_inclination", "51.6 deg")

    @pytest.mark.parametrize(
        ("override", "expected"),
        [
            (Override.length("a", 1), "1.0 m"),
            (Override.area("b", 2), "2.0 m^2"),
            (Override.mass("c", 3), "3.0 kg"),
            (Override.time("d", 4), "4.0 s"),
            (Override.frequency("e", 5), "5.0 Hz"),
            (Override.angle("f", 6), "6.0 deg"),
            (Override.power("g", 7), "7.0 W"),
            (Override.velocity("h", 8), "8.0 m/s"),
        ],
    )
    def test_convenience_constructors_use_expected_default_units(
        self, override, expected
    ):
        assert override.value == expected

    def test_scalar_keeps_integer_representation(self):
        override = Override.scalar("mode_count", 9)

        assert override.value == "9"


class TestNormalizeOverrides:
    def test_none_normalizes_to_empty_dict(self):
        assert normalize_overrides(None) == {}

    def test_mapping_values_are_stringified(self):
        normalized = normalize_overrides({"isp": 320.0, "mode_count": 9})

        assert normalized == {"isp": "320.0", "mode_count": "9"}

    def test_override_iterable_normalizes_to_name_value_dict(self):
        normalized = normalize_overrides(
            [
                Override.length("parking_orbit_altitude", 410.0, "km"),
                Override.angle("target_inclination", 51.6, "deg"),
            ]
        )

        assert normalized == {
            "parking_orbit_altitude": "410.0 km",
            "target_inclination": "51.6 deg",
        }

    def test_iterable_of_non_overrides_raises_type_error(self):
        with pytest.raises(TypeError):
            normalize_overrides(["isp=320.0 s"])
