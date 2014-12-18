---
layout: default
title: 
---
# Explore spatialite and create a database

## A word about spatialite
We are about to create a spatialite database for routing. [Spatialite](https://www.gaia-gis.it/fossil/libspatialite/index) is an extension for the [sqlite](http://www.sqlite.org/) database.
Sqlite is not a common RDMS in the sense that we are used to client-server databases like Postgresql or MySQL. Sqlite works as a library you use into your application, which produces local files (eg routing.sqlite). 
There is no need to install a database system, all you have to do is deploying the application. The only downside is that the spatialite extension to sqlite is not trivial to install on some platforms because of the numerous dependencies.


## Create the database

### Download OSM data

You can download OpenStreeMap data from [Geofabrik](http://download.geofabrik.de/) which gracefully give access to several geographic zones.

We'll work on the suburban area around Paris called Île-de-France. You can download the ile-de-france.osm.pbf file on [this page](http://download.geofabrik.de/europe/france/ile-de-france.html).

If you want faster computations, you can use a smaller data set from a small country such as Monaco.

### Create the routing enabled database
In order to set-up a database that is suitable for routing computation, you will need to insert all the roads in the database with the [spatialite_osm_net](https://www.gaia-gis.it/fossil/spatialite-tools/wiki?name=spatialite_osm_net) command line utility, part of the spatialite-tools we installed from spatialite-bin package.

    spatialite_osm_net -o  ile-de-france.osm.pbf -d routing.sqlite -T roads -m

That was not so long ! 

This command line have created a routing.sqlite file which contains a table roads with all the roads. Some extra tables contains some geographic metadata. You can have a look at the data with [QGis](http://www.qgis.org), by adding a spatialite layer to your workspace with button TODO screenshot.

In this model, roads are arcs, and we will compute routes between nodes : the vertices at both end of a road.

Back to the command line, prepare to wait much longer for the next step : 
creation of the network with the internal data structure suitable for routing algorithms.

    spatialite_network --db-path routing.sqlite --table roads --from-column node_from --to-column node_to --geometry-column geometry --a-star-supported  --name-column name --bidirectional --output-table net_data

More options are available to generate an oriented graph, to specify a specific cost for each arc (by default, we use the length of the geometry).
You can also use the spatialite-gui tool as described on the [spatialite wiki](https://www.gaia-gis.it/fossil/spatialite-tools/wiki?name=spatialite_osm_net).

Now, the network is inside the database, but we cannot make queries yet.
Let's open the spatialite console for the next operations :

    spatialite routing.sqlite

Spatialite's routing capabilities are provided through a *virtual* table. So we have to create it :

    CREATE VIRTUAL TABLE network USING VirtualNetwork(net_data);
    
The previous command has loaded the network graph in memory, which means it is now available for our first query :

    SELECT * FROM network WHERE NodeFrom = 123255457 AND NodeTo = 1430982681;

Tada !
	
Maybe you are not working on Ile-de-France, or maybe the nodes have disappeared for any reason. You can pick some random node ids by this query :

    SELECT node_from FROM roads LIMIT 10;

### Explore routing capabilities

This query provides the shortest path, but it is slow, because it uses the Dijkstra algorithm. 

With spatialite, we can specify that we want to use the `A*` (astat) algorithm, way faster, which give very good results on real networks.

    UPDATE idf_net SET Algorithm = "A*";
    
We can see duration of the queries in the spatialite console by enbabling time measurment

    .timer ON
And make our query again

    SELECT * FROM idf_net WHERE NodeFrom = 123255457 AND NodeTo = 1430982681;
     
Now the processing time is reasonable !

## A dirty trick
We have set up spatialite so that it computes routes with the Astar algorithm, as we can see :

    SELECT Algorithm from idf_net;

Now let's quit the spatialite console and get back in it, and check the configuration again :

    .exit
    spatialite routing.sqlite
    SELECT Algorithm from idf_net;

What has happened ?

Regular SQL users expect permanent modifications in table when we update them. But idf_net is not a table, it is a *virtual* table. 

This strange feature is here to provide a connection wide setting so that several concurrent user can use whatever algorithm they want.
So the trick was to implement this surprising column in memory... Which is not very consistent with SQL syntax.

Also : be careful with automatic memory management, because if spatialite needs memory, it may unload the virtual table, which will be recreated next time it is used... With the default algorithm (ie Dijstra)


## A note about Dijkstra and Astar

[Dijkstra algorithm](http://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) computes the shortest path between two nodes in a graph database where every connection has a positive cost (in our case, the cost is the length of the line).

The algorithm scans every node from the graph in order of increasing distance from the departure. Thus, it explores nodes in every direction. The algorithm stops when it finds the arrival node : no shortest path exists.

That's where Astar comes in action : this algorithms examines nodes preferentially in the direction of the arrival and stops when it gets to it. This is way faster !

## Creating a spatial index

Spatialite implements spatial index with `R*Tree` approach to speed up some queries, like finding the nearest node to start the route with.
So the final command we have to run in spatialite console, in order to prepare future location queries :

    SELECT CreateSpatialIndex('roads', 'geometry');
    
This command creates a table `idx_roads_geometry` which contains the bounding box of each road (with road ids). Section [Compute routes on the server](server2.html) describes how to take advantage of it.
