import json
import pandas as pd 
import numpy as np 
import geopy
import geopandas as gpd
import math
import geopy.distance
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle, VincentyDistance
from shapely.geometry import MultiPoint, Point
import plotly.express as px
import pygeohash as gh


def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster , key=lambda point: great_circle(point , centroid).m)
    return tuple(centermost_point)

class GridHelper():
    def DBSCAN_gen(self, df, epsilon=1.6):
        df = df[['lat', 'lon']]
        df = df[df['lat'] != '']
        df['lat'] = df['lat'].astype(float)
        df['lon'] = df['lon'].astype(float)

        coords = df.to_numpy(columns = ['lat', 'lon'])
        kms_per_radian = 6371.0088
        epsilon = epsilon / kms_per_radian
        db = DBSCAN(
            eps = epsilon, 
            min_samples = 1, 
            algorithm = 'ball_tree', 
            metric = 'haversine'
        ).fit(np.radians(coords))
        cluster_labels = db.labels_
        num_clusters = len(set(cluster_labels))
        clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])

        print ('number of clusters: {}'.format(num_clusters))

        centermost_points = clusters.map(get_centermost_point)

        lats, lons = zip(*centermost_points)
        rep_points = pd.DataFrame({'lon':lons, 'lat':lats})
        return rep_points

    def gen_grid(self, country, gap=3, output='dict'):
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        try:
            polies = world[world['name'].str.contains(country)]['geometry'].to_list()[0]
        except Exception as e:
            print (f'A problem occurred while finding {country} in world')
            print (e)

        min_lat = polies.bounds[1]
        min_lon = polies.bounds[0]
        max_lat = polies.bounds[3]
        max_lon = polies.bounds[2]

        lon_span = int(geopy.distance.vincenty((min_lat, min_lon), (min_lat, max_lon)).km)
        lat_span = int(geopy.distance.vincenty((min_lat, min_lon), (max_lat, min_lon)).km)

        # This method gives grid where points are {inc}km away from each other
        inc = gap * math.sqrt(2)
        lat_diff = (max_lat - min_lat)
        lon_diff = (max_lon - min_lon)
        lat_inc = lat_diff / lat_span * inc
        lon_inc = lon_diff / lon_span * inc

        # gen grids within rectangular area
        results = []
        for lat_index in range(int(lat_span/gap)):
            lat = min_lat + (lat_index * lat_inc)
            for lon_index in range(int(lon_span/gap)):
                lon = min_lon + (lon_index * lon_inc)
                _point = {'lat': lat, 'lon': lon}
                results.append(_point)

        # filter grids in actual country boundary
        points = []
        for point in results:
            _point = Point(point['lon'], point['lat'])
            if polies.contains(_point):
                points.append(point)

        results = {}
        results['dict'] = points

        js = {'data': points}
        results['json'] = js

        df = pd.DataFrame(points)
        results['df'] = results['dataframe'] = df

        return results[output]

    def geohash_grid(self, general_grid, data):
        general_grid['geohash'] = general_grid.apply(lambda x: gh.encode(x.lat, x.lon, precision=6), axis=1)
        data['geohash'] = data.apply(lambda x: gh.encode(x.lat, x.lon, precision=6), axis=1)
        result = general_grid[general_grid['geohash'].isin(data['geohash'])]
        return result

    def map_grid(self, df, zoom=3):
        if not isinstance(df, pd.DataFrame):
            print ('Input is not a pandas dataframe')
            return
        fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom = zoom, height=300)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.show()

