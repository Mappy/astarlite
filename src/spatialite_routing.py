#!/usr/bin/python

from pysqlite2 import dbapi2 as sqlite

class Routing:
    def __init__(self, db):
        self.conn = sqlite.connect(db)
        self.conn.enable_load_extension(True)
        self.conn.load_extension("libspatialite.so.3")
        cur = self.conn.cursor()
        query = 'UPDATE roads_net SET algorithm="A*"'
        cur.execute(query)
        cur.close()

    def compute_route(self, lat_from, lng_from, lat_to, lng_to):
        node_from = self.get_nearest_node(lat_from, lng_from)
        node_to = self.get_nearest_node(lat_to, lng_to)
        if node_to == None or node_from == None:
            return ""       
        cur = self.conn.cursor()
        query = 'SELECT askml(geometry) FROM "roads_net" where nodeFrom=? and nodeTo=? limit 1'
        cur.execute(query, (node_from, node_to))
        rec = cur.fetchone()
        cur.close()
        return rec[0]
            
    # Limit the search to 100 m
    def get_nearest_node(self, lat, lng):
        cur = self.conn.cursor()
        query = """
            SELECT 
                node_from, node_to, 
                ST_Distance(MakePoint({lng}, {lat}), PointN(geometry, 1)) as dist_node_from, 
                ST_Distance(MakePoint({lng}, {lat}), PointN(geometry, NumPoints(geometry))) as dist_node_to
            FROM roads 
            WHERE ROWID IN 
            (  SELECT pkid
                    FROM idx_roads_geometry
               WHERE xmin < {lng} + 0.001 AND xmax > {lng} - 0.001
                    AND ymin < {lat} + 0.001 AND ymax > {lat} - 0.001
            )
            ORDER BY Distance(MakePoint({lng}, {lat}), geometry)
            LIMIT 1
        """.format(lat = lat, lng = lng)
        cur.execute(query)
        rec = cur.fetchone()        
        cur.close()
        if rec == None:
            return None
        if rec[2] < rec[3]:
            return rec[0]
        else:
            return rec[1]

    def get_extent(self):
        cur = self.conn.cursor()
        query = """
            SELECT 
				X(PointN(linestring_bbox, 1)) as minx, 
				Y(PointN(linestring_bbox, 1)) as miny, 
				X(PointN(linestring_bbox, 3)) as maxx, 
				Y(PointN(linestring_bbox, 3)) as maxy 
				FROM (
					SELECT ST_Transform(
						ExteriorRing(SetSrid(Extent(geometry), 4326)), 
					  3785) as linestring_bbox FROM roads
				)
        """
        cur.execute(query)
        rec = cur.fetchone()
        res = { 'minx' : rec[0], 'miny' : rec[1], 'maxx' : rec[2], 'maxy' : rec[3] }
        return res
