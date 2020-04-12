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

        coords = df.as_matrix(columns = ['lat', 'lon'])
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