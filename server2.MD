---
layout: default
---

# Compute the route on the server

In this section, we will create a class ``Routing`` that will compute the actual routing

 
## Install spatialite driver for python

Unfortunately, the default sqlite python module shipped with Ubuntu forbids to load external extensions, because it might allow malicious use to load binary code from sql commands.
So we first have to install the proper driver :

    sudo apt-get install pysqlite2



## Init the database connection

Now we can create spatialite_routing.py with init code :

    #!/usr/bin/python

    from pysqlite2 import dbapi2 as sqlite

    class Routing:
        def __init__(self, db):
            self.conn = sqlite.connect(db)
            self.conn.enable_load_extension(True)
            self.conn.load_extension("libspatialite.so.3")

You have noticied that we have to willingly enable the loading of extentions, before we load spatialite. libspatialite.so.3 is the name of the linux library. If the library is not availlable in your PATH because you compiled it yourself or have an exotic install or you are working on windows, you can set the full path here.

We will also append to the init function the code to select the routing algorithm, as we have seen in preparing data TODO : lien

            cur = self.conn.cursor()
            query = 'UPDATE roads_net SET algorithm="A*"'
            cur.execute(query)
            cur.close()
        
## Get the nearest node
The client will query the route with latitude and longitude, so the first step is to get the id of the nearest node from where the user clicked.

Let's suppose the user clicked on Paris (Lat = 48.85, Long = 2.35). A naive aproche is the following sql query

    SELECT * FROM roads 
    ORDER BY 
        ST_Distance(geometry, MakePoint(2.35, 48.85)) 
    LIMIT 1

The function ST_Distance is provided by spatialite. This query scans every row from the roads table, computes the distance from the constant point MakePoint(2.35, 48.85), sorts the lines according to that distance, and keeps only one line : the nearest.

This query, indeed, provides the correct answer, but is very slow because sqlite has to evaluate the distance for each row of the table.

We can take advantage of the spatial index we created on the database.
The purpose of the user is to compute a route between two points. We can easily decide that if there is no node near enought, let's say 100m, it's not meaningfull to compute the route.

So we will select roads that are at distance of 0.001 degre (about 110 m), using the spatial index, wich makes the query 100 times faster :

    SELECT *
    FROM idx_roads_geometry
    WHERE xmin < 2.35  + 0.001 AND xmax > 2.35  - 0.001
      AND ymin < 48.85 + 0.001 AND ymax > 48.85 - 0.001

Now we only have a few candidates to examine, so we can order roads by distance to retreive the closest one :

    SELECT 
        node_from
    FROM roads 
    WHERE ROWID IN 
    (  SELECT pkid
            FROM idx_roads_geometry
       WHERE xmin < 2.35 + 0.001 AND xmax > 48.85 - 0.001
            AND ymin < 2.35 + 0.001 AND ymax > 48.85 - 0.001
    )
    ORDER BY Distance(MakePoint(2.35, 48.85), geometry)
    LIMIT 1

At last, we want to know wich end of the road is the closest, so we compute the distance to both of them, and we'll let the application chose :

    SELECT 
        node_from, node_to, 
        ST_Distance(MakePoint(2.35, 48.85), PointN(geometry, 1)) as dist_node_from, 
        ST_Distance(MakePoint(2.35, 48.85), PointN(geometry, NumPoints(geometry))) as dist_node_to
    FROM roads 
    WHERE ROWID IN 
    (  SELECT pkid
            FROM idx_roads_geometry
       WHERE xmin < 2.35 + 0.001 AND xmax > 48.85 - 0.001
            AND ymin < 2.35 + 0.001 AND ymax > 48.85 - 0.001
    )
    ORDER BY Distance(MakePoint(2.35, 48.85), geometry)
    LIMIT 1

This is the query we parametrise and integrate in the function get_nearest_node in module spatialite_routing.


## Compute the route
We can use the same query as earlier to compute the route between two nodes in our graph. We keep only the first raw, which sums up the whole route, and convert it to kml (a convenient format for web mapping) thanks to askml() function from spatialite.

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

Note that the question marks are replaced by the sqlite driver with the parameters `node_from` and `node_to` provided to the execute function.  
These parameters are properly escaped, which means do not have to worry about sql injections, even with text.

We can integrate this new function in server.py :

    @route('/route/<lat_from:float>,<lng_from:float>/<lat_to:float>,<lng_to:float>')
    def route(lat_from, lng_from, lat_to, lng_to):
        path = routing.compute_route(lat_from, lng_from, lat_to, lng_to)
        return template("template.kml", path=path)
            

    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("database")
        args = parser.parse_args()
        routing = Routing(args.database)
        print "Running server with database {}".format(args.database)
        run(host='localhost', port=8080, debug=True)

Now, run the server and see [http://localhost:8000/route/48.85,3.35/48.90,2.40](http://localhost:8000/route/48.85,3.35/48.90,2.40)...

