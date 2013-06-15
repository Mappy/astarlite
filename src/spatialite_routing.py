#!/usr/bin/python

from pysqlite2 import dbapi2 as sqlite

class Routing:
    def __init__(self, db):
        self.conn = sqlite.connect(db)
        self.conn.enable_load_extension(True)
        self.conn.load_extension("libspatialite.so.3")

    def compute_route(self, lat_from, lng_from, lat_to, lng_to):
        node_from = self.get_nearest_node(lat_from, lng_from)
        node_to = self.get_nearest_node(lat_to, lng_to)
        if node_to != None and node_from != None:
            return self.route_db_query(node_from, node_to)
        else:
            return ""

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

    def get_center(self):
        cur = self.conn.cursor()
        query = """
            SELECT X(center) as x, Y(center) as y FROM (
                SELECT ST_Transform(
                    SetSrid(Centroid(Extent(geometry)), 4326), 
                  3785) as center FROM roads
            )
        """
        cur.execute(query)
        rec = cur.fetchone()
        return rec

    def route_db_query(self, node_from, node_to):
        cur = self.conn.cursor()
        query = 'SELECT askml(geometry) FROM "roads_net" where nodeFrom=? and nodeTo=? limit 1'
        cur.execute(query, (node_from, node_to))
        rec = cur.fetchone()
        cur.close()
        return rec[0]
