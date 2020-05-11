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

    def map_grid(self, df):
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        world['name'].unique()
        tmp = pd.DataFrame.from_dict(df)
        gdf = gpd.GeoDataFrame(tmp, geometry=gpd.points_from_xy(tmp.lon, tmp.lat))
        ax = world.plot(color='white', edgecolor='black',figsize=(24, 24))
        gdf.plot(ax=ax, color='red',figsize=(24, 24))

    def gen_grid(self, country, gap=3, output='dict'):
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        polies = world[world['name'].str.contains(country)]['geometry'].to_list()[0]

        min_lat = polies.bounds[1]
        min_lon = polies.bounds[0]
        max_lat = polies.bounds[3]
        max_lon = polies.bounds[2]

        lon_span = int(geopy.distance.vincenty((min_lat, min_lon), (min_lat, max_lon)).km)
        lat_span = int(geopy.distance.vincenty((min_lat, min_lon), (max_lat, min_lon)).km)

        lat_diff = (max_lat - min_lat)
        lon_diff = (max_lon - min_lon)
        lat_inc = lat_diff / lat_span * gap
        lon_inc = lon_diff / lon_span * gap

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

