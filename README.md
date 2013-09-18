astarlite
=========

This tutorial, largely inspired from the pgRouting workshop will explain routing capabilities of sqlite databases througth the spatialite module.

# Pre-process a database

## Download data

You can download OpenStreeMap data from Cloudmade which gracefully give access to several zones.

We'll work on the suburban area around Paris called Île-de-France. You can download the ile-de-france.osm.bz2 file on http://downloads.cloudmade.com/europe/western_europe/france/ile-de-france#downloads_breadcrumbs using download_data.sh
(If you want faster results, you can use a smaller data set such as Monaco)

## Install dependencies

### On Ubuntu
    sudo apt-get install sqlite3 libspatialite3 spatialite3 spatialite-binspatialite-gui python-pysqlite2

### On Windows
One can try to install binaries from http://www.gaia-gis.it/gaia-sins/ under MS Windows binaries section. A simple alternative is to use a VM [(see below)](#virtualmachin) 

### On Mac OSX
MacPorts are too old (spatialite version is 2.3.1), compiling libspatialite is not straightforward (since you need proj4 and geos), a better option is to use a VM [(see below)](#virtualmachin)

### <a id="virtualmachin"></a>Using a Virtual Machine
Go to http://live.osgeo.org/en/download.html, download a virtual machine and follow the instructions here http://live.osgeo.org/en/quickstart/virtualization_quickstart.html
This distributions already contains libspatialite3 spatialite-bin

## Create the routing enabled database
Now, we'll set a database that is suitable for routing computation.

If you have not used download_data.sh, you need to decompress ile-de-france.osm.bz2

    bunzip2 ile-de-france.osm.bz2

We need to insert all the roads in the database thanks to the spatialite_osm_net command line interface, part of the spatialite-tools utilities, installed from spatialite-bin Ubuntu package.

    spatialite_osm_net -o  ile-de-france.osm -d routing.sqlite -T roads -m

Then, we create the network with the internal data structure for routing algorithms in spatialite

    spatialite_network --db-path routing.sqlite --table roads --from-column node_from --to-column node_to --geometry-column geometry --a-star-supported  --name-column name --bidirectional --output-table net_data

More options are avalables to generate an oriented graph, to specify a specific cost for each arc (by default, we use the length of the geometry).
You can also use the spatialite-gui tool as described on spatialite wiki : https://www.gaia-gis.it/fossil/spatialite-tools/wiki?name=spatialite_osm_net

Now, the network is inside the database, but we cannot make queries yet. We have to declare an interface that will use the data.

Open spatialite console

    spatialite routing.sqlite
    
Then create the virtual table that we'll be able to query for routes

    CREATE VIRTUAL TABLE idf_net USING VirtualNetwork(net_data);
    
The previous command loads the network graph in memory.

Now we can make our first query :

    SELECT * FROM idf_net WHERE NodeFrom = 123255457 AND NodeTo = 1430982681;

This query might be slow, because it uses the Dijkstra algorithm, which will stricty provide the shortest path.

We can specify that we want to use the A* algorithm, way faster, which give very good results on real networks.

    UPDATE idf_net SET Algorithm = "A*";
    
We can see duration of the queries in the spatialite console by enbabling time measurment

    .timer ON
And make our query again

    SELECT * FROM idf_net WHERE NodeFrom = 123255457 AND NodeTo = 1430982681;
     
Now the processing time is reasonable !
    
# A real Application

We'll make a web application in Python / javascript that let you compute routing by pointing departure and arrival on a map.

If you don't already have Python, you can follow instructions on the main page : http://www.python.org/

## Dependencies

    sudo pip install bottle

## Init the database connection

Unfortunately, the default sqlite python module shipped with Ubuntu forbids to load external extensions, because it might allow malicious use to load binary code from sql commands.
So we first have to install the proper driver :
    sudo apt-get install pysqlite2

Now we can create spatialite_routing.py to begin coding :

    #!/usr/bin/python

    from pysqlite2 import dbapi2 as sqlite

    class Routing:
        def __init__(self, db):
            self.conn = sqlite.connect(db)
            self.conn.enable_load_extension(True)
            self.conn.load_extension("libspatialite.so.3")

You've noticied that we have to willingly enable the loading of extentions, before we load spatialite. libspatialite.so.3 is the name of the linux library. If the library is not availlable in your PATH because you compiled it yourself or have a weired install, you can set the full path here.


## Get the nearest node
The client will query the route with latitude and longitude, so the first step is to get the id of the nearest node from where the user clicked.

Let's suppose the user clicked on Paris (Lat = 48.85, Long = 2.35). A naive aproche is the following sql query

    SELECT * FROM roads ORDER BY ST_Distance(geometry, MakePoint(2.35, 48.85)) LIMIT 1

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

Note that the question marks are replaced by the sqlite driver with the parameters `node_from` and `node_to` provided to the execute function.  These parameters are properly escaped, which means do not have to worry about sql injections, even with text.

The kml returned by this function (the record #0 of the only line) is not self-suffisant. It is intented to be inserted in a complete kml template.

## Display the availlable area on the map
We want the initial position of the map to be centered on the area which is available for routing, so we will have to compute the bounding box roads.
The spatialite function `Extent()` is an aggregate, which means it returns one result for all the rows, exactly like the `max()` or the `count()` functions. Here, it computes a geomtry which is the bounding box of all geomtries from the table :

    SELECT Extent(geometry) FROM roads

Unfortunately, this does not give us directly the xmin, xmax, ymin and ymax values.

The extent is a Polygon geometry, and Polygons can have holes in spatialite. So we need extract what is called the exterior ring :

    SELECT ExteriorRing(Extent(geometry)) as linestring_bbox FROM roads;


The result is a Linestring geometry.

Now we can acces the points from the Linestring with the ''PointN()'' function, which indices are 1-based (instead of 0-based like arrays in many languages), and get the X() and the Y() values of these points :

    SELECT 
        X(PointN(linestring_bbox, 1)) as minx, 
        Y(PointN(linestring_bbox, 1)) as miny, 
        X(PointN(linestring_bbox, 3)) as maxx, 
        Y(PointN(linestring_bbox, 3)) as maxy 
        FROM (
            SELECT 
                ExteriorRing(Extent(geometry))as linestring_bbox 
            FROM roads
        )

We still have one more operation to do. OpenLayers, the javascript libray we use to display the route will display an OSM map. 
Unforunately this map will not accept coordinates in latitude and longitude, but in another coordinate system which is common in sofware maping : it has the same mercator look, but coordinates are in meters rather than in degrees of arc.
So we have to convert the bounding box from coordinate system (CS) 4326 to CS 3785.
In order to to that, we have to tell spatialite that our previous result has to be considered in CS 4326 with function ''SetSrid()'' and convert it with function ''ST_Transform()'' :

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

Here we are, at last !

## Create a server
A small server file server.py is availlable in the source tree. It uses a framework called Bottle that provides easy matching of urls to functions and templating :




    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    
    from bottle import route, run, static_file, template
    from spatialite_routing import Routing
    import argparse
    
    routing = None
    
    @route('/')
    def index():
        center = routing.get_center()
        return template("index.html", center_x = center[0], center_y = center[1])
    
    @route('/js/<path:path>')
    def js(path):
        return static_file(path, root='js')
    
    @route('/route/<start>/<end>')
    def route(start, end):
        lat_from, lng_from = tuple(map(float, start.split(",")))
        lat_to, lng_to = tuple(map(float, end.split(",")))
        path = routing.compute_route(lat_from, lng_from, lat_to, lng_to)
        return template("template.kml", path=path)
            

    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("database")
        args = parser.parse_args()
        routing = Routing(args.database)
        run(host='localhost', port=8080, debug=True)

