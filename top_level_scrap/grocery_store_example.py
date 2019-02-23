# passed a dict with {'x': ..., 'y': ...}
# from get_ward_precinct_info
from pprint import pprint

import requests

# base_url = "https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services/Precincts_2017/FeatureServer/0/query"
grocery_url = "https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services/Supermarkets_GroceryStores/FeatureServer/0/query"


ESRI_SPATIAL_REFERENCE = 3857
LAT_LONG_SPATIAL_REFERENCE = 4326
KM_UNIT = 'esriSRUnit_Kilometer'
MILE_UNIT = 'esriSRUnit_StatuteMile'

star_market_esri = {'x': -7912519.379350758, 'y': 5213279.94167787}
star_market_lon_lat = {'x': -71.0793703469, 'y': 42.3481798771}
trader_joe_lon_lat = {'x': -71.0841200722, 'y': 42.3485000974}


params = {
    "f": "json",
    "geometry": str(trader_joe_lon_lat['x']) + "," + str(trader_joe_lon_lat['y']),
    "geometryType": "esriGeometryPoint",
    "returnGeometry": "true",
    "inSR": "{}".format(LAT_LONG_SPATIAL_REFERENCE),
    "outSR": LAT_LONG_SPATIAL_REFERENCE,
    "where": "1=1",
    "outFields": "Lat,Lon",
    "distance": "0.001",
    "units": KM_UNIT
}

response = requests.request("GET", grocery_url, params=params)

pprint(response.json())

print(isinstance(response.json(), dict))
