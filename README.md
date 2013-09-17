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

This query, indeed, provides the correct answer, but is very slow because sqlite has to evaluate the distance for each row.

We can take advantage of the spatial index we created on the database.
The purpose of the user is to compute a route between two points. We can easily decide that if there is no node near enought, it's not meaningfull to compute the route.

It doesn't seam meaningfull for a 



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

