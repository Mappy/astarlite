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
        kml = self.route_db_query(node_from, node_to)
        return kml

    def get_nearest_node(self, lat, lng):
        cur = self.conn.cursor()
        query = """SELECT node_from  
        FROM roads 
        order by distance(geometry, PointFromText('Point({} {})')) limit 1
        """.format(lat, lng)
        cur.execute(query)
        rec = cur.fetchone()
        return rec[0]

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

    def close(self):        
        self.conn.close()

    def route_db_query(self, node_from, node_to):
        cur = self.conn.cursor()
        query = 'SELECT askml(geometry) FROM "roads_net" where nodeFrom=? and nodeTo=? limit 1'
        cur.execute(query, (node_from, node_to))
        rec = cur.fetchone()
        return rec[0]
