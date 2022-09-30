import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon

from .coordTransform import wgs84_to_bd09, wgs84_to_gcj02
from .coordTransform import gcj02_to_bd09, gcj02_to_wgs84
from .coordTransform import bd09_to_wgs84, bd09_to_gcj02


def polyline_wgs_to_gcj(gdf):
    '''
    transfer the shapfile coordination system
    '''
    gdf['geometry'] = gdf.apply(lambda i: LineString(pd.DataFrame(i.geometry.coords.xy).T.rename(
        columns={0: 'x', 1: 'y'}).apply(lambda x: wgs84_to_gcj02(x.x, x.y), axis=1)), axis=1)
    return gdf


def polyline_gcj_to_wgs(gdf):
    '''
    transfer the shapfile coordination system
    '''
    gdf['geometry'] = gdf.apply(lambda i: LineString(pd.DataFrame(i.geometry.coords.xy).T.rename(
        columns={0: 'x', 1: 'y'}).apply(lambda x: gcj02_to_wgs84(x.x, x.y), axis=1)), axis=1)
    return gdf


# new function
def _gdf_wgs_to_gcj(gdf):
    '''
    transfer the shapfile coordination system
    '''
    if isinstance(gdf.iloc[0].geometry, Polygon):
        gdf['geometry'] = gdf.apply(lambda i: Polygon(pd.DataFrame(i.geometry.exterior.coords.xy).T.rename(
            columns={0: 'x', 1: 'y'}).apply(lambda x: wgs84_to_gcj02(x.x, x.y), axis=1)), axis=1)
    elif isinstance(gdf.iloc[0].geometry, LineString):
        gdf['geometry'] = gdf.apply(lambda i: LineString(pd.DataFrame(i.geometry.coords.xy).T.rename(
            columns={0: 'x', 1: 'y'}).apply(lambda x: wgs84_to_gcj02(x.x, x.y), axis=1)), axis=1)
    elif isinstance(gdf.iloc[0].geometry, MultiPolygon):
        gdf['geometry'] = gdf.geometry.apply(lambda item: MultiPolygon([ Polygon(pd.DataFrame( geom.exterior.coords.xy ).T.rename(columns={0: 'x', 1: 'y'}).apply( lambda x: wgs84_to_gcj02(x.x, x.y), axis=1)) for geom in item.geoms]) )
    elif isinstance(gdf.iloc[0].geometry, Point):
            gdf['geometry'] = gdf.apply(lambda i: Point(wgs84_to_gcj02(i.geometry.x, i.geometry.y)), axis=1)
    return gdf


def _gdf_gcj_to_wgs(gdf):
    '''
    transfer the shapfile coordination system
    '''
    if isinstance(gdf.iloc[0].geometry, Polygon):
        gdf['geometry'] = gdf.apply(lambda i: Polygon(pd.DataFrame(i.geometry.exterior.coords.xy).T.rename(
            columns={0: 'x', 1: 'y'}).apply(lambda x: gcj02_to_wgs84(x.x, x.y), axis=1)), axis=1)
    elif isinstance(gdf.iloc[0].geometry, LineString):
        gdf['geometry'] = gdf.apply(lambda i: LineString(pd.DataFrame(i.geometry.coords.xy).T.rename(
            columns={0: 'x', 1: 'y'}).apply(lambda x: gcj02_to_wgs84(x.x, x.y), axis=1)), axis=1)
    elif isinstance(gdf.iloc[0].geometry, MultiPolygon):
        gdf['geometry'] = gdf.geometry.apply(lambda item: MultiPolygon([ Polygon(pd.DataFrame( geom.exterior.coords.xy ).T.rename(columns={0: 'x', 1: 'y'}).apply( lambda x: gcj02_to_wgs84(x.x, x.y), axis=1)) for geom in item.geoms]) )
    elif isinstance(gdf.iloc[0].geometry, Point):
            gdf['geometry'] = gdf.apply(lambda i: Point(gcj02_to_wgs84(i.geometry.x, i.geometry.y)), axis=1)
    return gdf


def gdf_bd_to_wgs(gdf):
    '''
    transfer the shapfile coordination system
    '''
    if isinstance(gdf.iloc[0].geometry, Polygon):
        gdf['geometry'] = gdf.apply(lambda i: Polygon(pd.DataFrame(i.geometry.exterior.coords.xy).T.rename(
            columns={0: 'x', 1: 'y'}).apply(lambda x: bd09_to_wgs84(x.x, x.y), axis=1)), axis=1)
    elif isinstance(gdf.iloc[0].geometry, LineString):
        gdf['geometry'] = gdf.apply(lambda i: LineString(pd.DataFrame(i.geometry.coords.xy).T.rename(
            columns={0: 'x', 1: 'y'}).apply(lambda x: bd09_to_wgs84(x.x, x.y), axis=1)), axis=1)
    elif isinstance(gdf.iloc[0].geometry, MultiPolygon):
        gdf['geometry'] = gdf.geometry.apply(lambda item: MultiPolygon([ Polygon(pd.DataFrame( geom.exterior.coords.xy ).T.rename(columns={0: 'x', 1: 'y'}).apply( lambda x: bd09_to_wgs84(x.x, x.y), axis=1)) for geom in item.geoms]) )
    elif isinstance(gdf.iloc[0].geometry, Point):
            gdf['geometry'] = gdf.apply(lambda i: Point(bd09_to_wgs84(i.geometry.x, i.geometry.y)), axis=1)
    return gdf


def transform_gdf_coord_sys(gdf, in_sys='gcj', out_sys='wgs'):
    assert in_sys in ['gcj', 'wgs'] and in_sys in ['gcj', 'wgs'], "check coord sys"
    
    if in_sys != out_sys:
        if in_sys == 'gcj':
            gdf = _gdf_gcj_to_wgs(gdf)
        else:
            gdf = _gdf_wgs_to_gcj(gdf)
    
    return gdf


def df_to_gdf_points( trip, in_sys = 'gcj', out_sys = 'wgs', keep_datetime =True ):
    if not keep_datetime and len(trip.dtypes[trip.dtypes == 'datetime64[ns]'].index)>0:
        trip = trip.drop(columns = trip.dtypes[trip.dtypes == 'datetime64[ns]'].index)
    # gpd.GeoDataFrame(trip, geometry=  trip.apply( lambda x: Point( x.x, x.y ),axis=1)).to_file( f'{plate}.geojson', driver='GeoJSON' )
    trip = gpd.GeoDataFrame( trip, geometry = trip.apply( lambda x: Point( x.x, x.y ),axis=1), crs={'init':'epsg:4326'})
    trip = transform_gdf_coord_sys( trip, in_sys, out_sys )
    return trip


def traj_points_to_line( df_tra, df_trip, plate, save = False ):
    # TODO
    gdf = gpd.GeoDataFrame()
    for i in df_trip.trip_id.unique():
        tra = LineString( df_tra[df_tra.trip_id==i][['x','y','t']].values )
        gdf = gdf.append( {'trip_id':i, 'geometry':LineString( df_tra[df_tra.trip_id==i][['x','y','t']].values ) }, ignore_index=True)
    gdf = gdf.merge( df_trip, on ='trip_id' )
    gdf = _gdf_gcj_to_wgs( gdf )
    gdf.crs={'init':'epsg:4326'}
    # gdf.to_crs(epsg=4547) 
    if save:    gdf.to_file( '%s.shp'%(plate), encoding='utf-8' )
    return gdf


if __name__ == '__main__':
    # a = gpd.read_file('../trajectory_related/input/Futian_boundary_wgs.shp')
    df_to_gdf_points(trip)
    pass
