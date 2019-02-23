import unittest
from typing import Optional, List

from mycity.test.test_our_stuff.test_distance import Mile, Distance, Kilometer
from mycity.test.test_our_stuff.test_long_lat import LongLatPoint


class ArcGisParams(object):
    LAT_LONG_SPATIAL_REFERENCE = 4326

    def __init__(self, update_json: Optional[dict] = None):
        self._json = {
            "f": "json",
            "inSR": self.LAT_LONG_SPATIAL_REFERENCE,
            "outSR": self.LAT_LONG_SPATIAL_REFERENCE,
            "returnGeometry": "true",
            "outFields": "*",
        }
        if update_json:
            self._json.update(update_json)

    def get_json(self):
        return self._json.copy()

    def add_origin_point(self, origin: LongLatPoint):
        params = self
        if "distance" not in self._json:
            point_distance = Mile(0.001)
            params = self.add_distance(point_distance)
        origin_details = {
            "geometry": f"{origin.x},{origin.y}",
            "geometryType": "esriGeometryPoint",
        }
        return params._get_updated_params(origin_details)

    def add_distance(self, distance: Distance):
        unit = self._get_distance_units(distance)

        distance_details = {
            "distance": distance.value,
            "units": unit
        }
        return self._get_updated_params(distance_details)

    @staticmethod
    def _get_distance_units(distance):
        units = {
            Mile: "esriSRUnit_StatuteMile",
            Kilometer: "esriSRUnit_Kilometer"
        }
        try:
            unit = next((val for key, val in units.items() if isinstance(distance, key)))
        except StopIteration:
            raise ValueError(f"No esri units for type: {distance.__class__}")
        return unit

    def add_specific_outfields(self, out_fields: List[str]):
        out_fields_details = {
            "outFields": ",".join(out_fields)
        }
        return self._get_updated_params(out_fields_details)

    def add_all_outfields(self):
        updated_outfields = {"outFields": "*"}
        return self._get_updated_params(updated_outfields)

    def add_where(self, where_str: str):
        updated_where_str = {"where": where_str}
        return self._get_updated_params(updated_where_str)

    def _get_updated_params(self, update_json):
        to_update = self.get_json()
        to_update.update(update_json)
        return ArcGisParams(to_update)


class TestArcGISParams(unittest.TestCase):

    def test_init_default_params(self):
        expected_params = {
            "f": "json",
            "inSR": 4326,
            "outSR": 4326,
            "returnGeometry": "true",
            "outFields": "*",
        }
        params = ArcGisParams()
        actual_json = params.get_json()
        self.assertEqual(expected_params, actual_json)

    def test_get_json_returns_copy(self):
        params = ArcGisParams()
        original = params.get_json()
        original['test'] = 172389
        self.assertNotEqual(original, params.get_json())

    def test_init_with_new_params(self):
        expected_params = {
            "f": "json",
            "inSR": 4326,
            "outSR": 4326,
            "returnGeometry": "true",
            "outFields": "*",
            "test": "z"
        }
        params = ArcGisParams({"test": "z"})
        self.assertEqual(params.get_json(), expected_params)

    def test_init_with_new_params_changing_update_json_does_not_affect_json(self):
        expected_params = {
            "f": "json",
            "inSR": 4326,
            "outSR": 4326,
            "returnGeometry": "true",
            "outFields": "*",
            "test": "z"
        }
        update_json = {"test": "z"}
        params = ArcGisParams(update_json)
        update_json["test"] = "y"
        self.assertEqual(params.get_json(), expected_params)

    def test_init_with_update_json_existing_keys(self):
        update_json = {"inSR": 1}
        expected_params = {
            "f": "json",
            "inSR": 1,
            "outSR": 4326,
            "returnGeometry": "true",
            "outFields": "*",
        }
        params = ArcGisParams(update_json)
        self.assertEqual(params.get_json(), expected_params)

    def test_add_origin_point_no_distance(self):
        x = 1.0
        y = 2.0
        origin = LongLatPoint(x, y)

        expected_json = {
            "f": "json",
            "inSR": 4326,
            "outSR": 4326,
            "returnGeometry": "true",
            "outFields": "*",

            "geometry": f"{x},{y}",
            "geometryType": "esriGeometryPoint",
            "distance": 0.001,
            "units": "esriSRUnit_StatuteMile"
        }
        params = ArcGisParams().add_origin_point(origin)
        self.assertEqual(params.get_json(), expected_json)

    def test_add_origin_point_has_distance(self):
        x = 1.0
        y = 2.0
        origin = LongLatPoint(x, y)
        distance = 100.0
        units = "myUnits"

        expected_json = {
            "f": "json",
            "inSR": 4326,
            "outSR": 4326,
            "returnGeometry": "true",
            "outFields": "*",

            "geometry": f"{x},{y}",
            "geometryType": "esriGeometryPoint",
            "distance": distance,
            "units": units
        }
        params = ArcGisParams({"distance": distance, "units": units}).add_origin_point(origin)
        self.assertEqual(params.get_json(), expected_json)

    def test_add_origin_overwrite_old_origin(self):
        old_x, old_y = 1.0, 2.0
        new_x, new_y = 3.0, 4.0

        with_old_origin = ArcGisParams().add_origin_point(LongLatPoint(old_x, old_y))
        with_new_origin = with_old_origin.add_origin_point(LongLatPoint(new_x, new_y))

        new_json = with_new_origin.get_json()
        self.assertEqual(new_json['geometry'], f"{new_x},{new_y}")

    def test_add_origin_keeps_other_params(self):
        x, y = 1.0, 2.0
        test_update = {
            "test": "x",
            "inSR": 1
        }

        expected = {
            "f": "json",
            "inSR": 1,
            "outSR": 4326,
            "returnGeometry": "true",
            "outFields": "*",
            "test": "x",

            "geometry": f"{x},{y}",
            "geometryType": "esriGeometryPoint",
            "distance": 0.001,
            "units": "esriSRUnit_StatuteMile"
        }

        params = ArcGisParams(test_update).add_origin_point(LongLatPoint(x, y))
        self.assertEqual(params.get_json(), expected)

    def test_add_distance_mile(self):
        value = 2.0
        params = ArcGisParams()
        with_distance = params.add_distance(Mile(value))

        expected = params.get_json()
        distance_dict = {
            "distance": value,
            "units": "esriSRUnit_StatuteMile"
        }
        expected.update(distance_dict)
        self.assertEqual(with_distance.get_json(), expected)

    def test_add_distance_kilometer(self):
        value = 2.0
        params = ArcGisParams()
        with_distance = params.add_distance(Kilometer(value))

        expected = params.get_json()
        distance_dict = {
            "distance": value,
            "units": "esriSRUnit_Kilometer"
        }
        expected.update(distance_dict)
        self.assertEqual(with_distance.get_json(), expected)

    def test_add_distance_overwrites_distance(self):
        old_value = 2.0
        new_value = 1.0
        params = ArcGisParams()
        old_distance = params.add_distance(Mile(old_value))

        new_distance = old_distance.add_distance(Kilometer(new_value))

        expected = params.get_json()
        distance_dict = {
            "distance": new_value,
            "units": "esriSRUnit_Kilometer"
        }
        expected.update(distance_dict)
        self.assertEqual(new_distance.get_json(), expected)

    def test_add_distance_does_not_overwrite_other_values(self):
        added_field = {'test': 1}
        x, y = 1.0, 2.0
        with_origin = ArcGisParams(added_field).add_origin_point(LongLatPoint(x, y))

        mile_value = 3.0
        final = with_origin.add_distance(Mile(mile_value))
        final_json = final.get_json()
        self.assertEqual(final_json['test'], 1)

        distance_update = {"distance": mile_value, "units": "esriSRUnit_StatuteMile"}
        expected = with_origin.get_json()
        expected.update(distance_update)
        self.assertEqual(final_json, expected)

    def test_add_distance_not_Mile_or_Kilometer_raises_value_error(self):
        class TestDistance(Distance):
            @property
            def value(self):
                return 1.0

        self.assertRaises(ValueError, ArcGisParams().add_distance, TestDistance())

    def test_add_specific_outfields_single_field(self):
        out_fields = ['a']
        out_fields_str = 'a'
        params = ArcGisParams()
        with_outfields = params.add_specific_outfields(out_fields)

        expected = params.get_json()
        expected['outFields'] = out_fields_str
        self.assertEqual(with_outfields.get_json(), expected)

    def test_add_specific_outfields_multiple_fields(self):
        out_fields = ['a', 'b', 'c']
        out_fields_str = 'a,b,c'
        params = ArcGisParams()
        with_outfields = params.add_specific_outfields(out_fields)

        expected = params.get_json()
        expected['outFields'] = out_fields_str
        self.assertEqual(with_outfields.get_json(), expected)

    def test_add_specific_outfields_overwrites_old_outfields(self):
        old_outfields = ['a', 'b', 'c']
        params = ArcGisParams()
        with_old_outfields = params.add_specific_outfields(old_outfields)

        new_outfields = ['d', 'e']
        with_new_outfields = with_old_outfields.add_specific_outfields(new_outfields)

        expected = params.get_json()
        expected['outFields'] = ','.join(new_outfields)
        self.assertEqual(with_new_outfields.get_json(), expected)

    def test_add_specific_outfields_keeps_other_changes(self):
        out_fields = ['a', 'b', 'c']

        to_update = {'test': 'x'}
        params = ArcGisParams(to_update).add_distance(Mile(1.0))
        expected = params.get_json()
        expected['outFields'] = ','.join(out_fields)

        with_outfields = params.add_specific_outfields(out_fields)
        self.assertEqual(with_outfields.get_json(), expected)

    def test_add_all_outfields(self):
        old_outfields = ['a', 'b']
        params = ArcGisParams().add_specific_outfields(old_outfields)

        expected = params.get_json()
        expected['outFields'] = "*"

        all_outfields = params.add_all_outfields()
        self.assertEqual(all_outfields.get_json(), expected)

    def test_add_all_outfields_keeps_other_params(self):
        to_update = {'test': 'x'}
        old_outfields = ['a', 'b']
        params = ArcGisParams(to_update).add_specific_outfields(old_outfields).add_distance(Mile(1.0))

        expected = params.get_json()
        expected['outFields'] = "*"

        all_outfields = params.add_all_outfields()
        self.assertEqual(all_outfields.get_json(), expected)

    def test_add_where(self):
        where_string = "a = b"
        params = ArcGisParams()

        expected = params.get_json()
        expected['where'] = where_string

        where_params = params.add_where(where_string)
        self.assertEqual(where_params.get_json(), expected)

    def test_add_where_overwrite_old_where(self):
        old_where_string = "nope"
        new_where_string = "a = b"
        old_where = ArcGisParams().add_where(old_where_string)

        expected = old_where.get_json()
        expected['where'] = new_where_string

        new_where = old_where.add_where(new_where_string)
        self.assertEqual(new_where.get_json(), expected)

    def test_add_where_keeps_other_params(self):
        where_string = "a = b"

        to_update = {'test': 'x'}
        params = ArcGisParams(to_update).add_distance(Mile(1.0))

        expected = params.get_json()
        expected['where'] = where_string

        all_outfields = params.add_where(where_string)
        self.assertEqual(all_outfields.get_json(), expected)
