import unittest

import requests

from mycity.test.test_our_stuff.test_distance import Mile, Distance
from mycity.test.test_our_stuff.test_long_lat import LongLatPoint
from mycity.test.test_our_stuff.test_params import ArcGisParams

ARCGIS_GROCERY_URL = "https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services/Supermarkets_GroceryStores/FeatureServer/0/query"

"""
[{'attributes': {'Address': '53 Huntington Avenue',
                 'Neighborho': 'Back Bay',
                 'Store': 'Star Market',
                 'Type': 'Supermarket'},
  'geometry': {'x': -71.07937094362696, 'y': 42.34818854754179}},
 {'attributes': {'Address': '899 Boylston Street',
                 'Neighborho': 'Back Bay',
                 'Store': "Trader Joe's",
                 'Type': 'Supermarket'},
  'geometry': {'x': -71.08412067057046, 'y': 42.34850876773183}},
 {'attributes': {'Address': '15 Westland Avenue',
                 'Neighborho': 'Fenway',
                 'Store': 'Whole Foods Market',
                 'Type': 'Supermarket'},
  'geometry': {'x': -71.08655092017358, 'y': 42.34368825128806}}]

"""

# TODO review code logic
# TODO distance as a parameter to get_grocery_store_api_response
# TODO discuss using mocks for "requests"
# TODO error_handling response.status_code != 200
# TODO error_handling response.json()['features'] == []


ACTUAL_BOSTON_GROCERY_STORE_LONGLAT_COORDINATES = (-71.0793703469, 42.3481798771)


class ArcGisGroceryRequest(object):
    arc_gis_url = ARCGIS_GROCERY_URL

    def __init__(self, origin_point: LongLatPoint):
        self._origin_point = origin_point

    def get_nearby(self, distance: Distance):
        out_fields = ('Address', 'Neighborho', 'Store', 'Type')
        params_obj = ArcGisParams()
        params_obj = params_obj.add_origin_point(self._origin_point).add_distance(distance)
        params_obj = params_obj.add_specific_outfields(out_fields)

        response = requests.get(self.arc_gis_url, params=params_obj.get_json())
        features = response.json()['features']
        return features


class TestArcGisGroceryRequest(unittest.TestCase):
    def test_get_nearby_returns_list_of_dicts_with_set_keys(self):
        distance = Mile(0.5)
        origin = LongLatPoint(*ACTUAL_BOSTON_GROCERY_STORE_LONGLAT_COORDINATES)
        request_obj = ArcGisGroceryRequest(origin)

        response = request_obj.get_nearby(distance)

        expected_keys = ('attributes', 'geometry')
        expected_attribute_keys = ('Address', 'Neighborho', 'Store', 'Type')
        for element in response:
            self.assertEqual(sorted(element.keys()), sorted(expected_keys))
            self.assertEqual(sorted(element['attributes'].keys()), sorted(expected_attribute_keys))
