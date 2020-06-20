import geopandas as gpd
from shapely.geometry import Point, LineString
from fiona.crs import from_epsg
import math
import pandas as pd
import networkx as nx
import os

def get_shapefile_name(path):
    path = (['/'] if path[0] == '/' else []) + path.split('/')
    for file in os.listdir(os.path.join(*path)):
        if file.split('.')[-1] == 'shp':
            return os.path.join(*path, file)

def list_shapefile_names(path):
    path = (['/'] if path[0] == '/' else []) + path.split('/')
    ret = []
    for file in os.listdir(os.path.join(*path)):
        if file.split('.')[-1] == 'shp':
            ret.append(os.path.join(*path, file))
    return ret

def get_graph_from_gdf(gdf, cost, speed, road_type):
    graph = nx.MultiGraph()
    for _, row in gdf.iterrows():
        p1 = Point(list(row[0].coords)[0])
        p2 = Point(list(row[0].coords)[-1])
        length = p1.distance(p2)/1000
        dist = length * cost
        time_takes = length * speed
        graph.add_node((*p1.coords), name=row[2])
        graph.add_node((*p2.coords), name=row[1])
        graph.add_edge((*p1.coords), (*p2.coords), cost=dist, road=road_type, time=time_takes, src=row[2], dst=row[1])
    return graph

def read_route_csv(file):
    df = pd.read_csv(file, header=None, sep='\n')[0].str.split(',', expand=True).drop(columns=0)
    gdf = gpd.GeoDataFrame(columns=['roads', 'src', 'dst'], geometry='roads', crs=from_epsg(4326))
    for idx, row in df.iterrows():
        roads = []
        for i, item in enumerate(row):
            if i % 2 == 1:
                continue
            try:
                float(item)
                roads.append((float(row[i+1]), float(row[i+2])))
            except ValueError:
                gdf = gdf.append({'roads': roads, 'src': row[i+1], 'dst': row[i+2]}, ignore_index=True)
                break
    gdf['roads'] = gdf['roads'].apply(lambda row: LineString([Point(item) for item in row]))
    gdf = gdf.to_crs(epsg=3106)
    return gdf

def convert_point_crs(px, py, fromepsg, toepsg):
    return list(gpd.GeoDataFrame([Point((px, py))], columns=['geometry'], crs=from_epsg(fromepsg)).to_crs(epsg=toepsg).iloc(0)[0][0].coords)[0]
   
def get_nearest_point(p, lines):
    min_dist = float('inf')
    for line in lines:
        point = line.interpolate(line.project(p))
        dist = point.distance(p)
        if dist < min_dist:
            min_dist = dist
            min_point = point
            dist1 = dist
            dist2 = line.length - dist1
            min_line = line
    
    for p1, p2 in zip(list(min_line.coords), list(min_line.coords)[1:]):
        l = LineString([p1, p2])
        p1 = Point(p1)
        p2 = Point(p2)
        
        if p1.distance(min_point) + p2.distance(min_point) - l.length < 1e-8:
            pl, pr = Point(p1), Point(p2)
            break
        
    return min_line, min_point, pl, pr, min_point.distance(Point(pl)), min_point.distance(Point(pr))
