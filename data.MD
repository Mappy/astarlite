---
layout: default
title: 
---
# Explore spatialite and create a database

## A word about spatialite
We are about to build a spatialite database for routing. [Spatialite](http://www.gaia-gis.it/gaia-sins/) TODO vérifier le lien is an extension for the [sqlite](bla) TODO : lien database.
Sqlite is not a common database in the sense that we are used to client-server databases like Postgresql or MySQL. Sqlite works as a library you use into your application, which produces local files (eg routing.sqlite). 
There is no need to install a server, only deploying the application is suffisent. The only downside is that the spatialite extension to sqlite is not trivial to install on some plateforms because of the numerous dependencies.


## Create the database
### Download OSM data

You can download OpenStreeMap data from [Cloudmade](http://downloads.cloudmade.com) which gracefully give access to several areas.

We'll work on the suburban area around Paris called Île-de-France. You can download the ile-de-france.osm.bz2 file on [http://downloads.cloudmade.com/europe/western_europe/france/ile-de-france#downloads_breadcrumbs](http://downloads.cloudmade.com/europe/western_europe/france/ile-de-france#downloads_breadcrumbs).
If you want faster computations, you can use a smaller data set such as the very small country called Monaco.

### Create the routing enabled database
In order to setup a database that is suitable for routing computation, you need to decompress ile-de-france.osm.bz2 (you will need 20 Go TODO vérifier of free disk space)

    bunzip2 ile-de-france.osm.bz2

We will insert all the roads in the database with the [spatialite_osm_net](http://TODO-lien-vers-la-doc) command line utility, part of the spatialite-tools we installed from spatialite-bin package.

    spatialite_osm_net -o  ile-de-france.osm -d routing.sqlite -T roads -m

That was not so long ! 

You can have a look at the data with [QGis](http://www.qgis.org), by adding a spatialite layer to your workspace with button TODO screenshot.
In our model, roads will be arcs, and we will compute routes between nodes : the vertex at both end of a road.

Back to the command line, prepare to wait much longer for the next step : 
creation of the network with the internal data structure suitable for routing algorithms.

    spatialite_network --db-path routing.sqlite --table roads --from-column node_from --to-column node_to --geometry-column geometry --a-star-supported  --name-column name --bidirectional --output-table net_data

More options are avalables to generate an oriented graph, to specify a specific cost for each arc (by default, we use the length of the geometry).
You can also use the spatialite-gui tool as described on the [spatialite wiki](https://www.gaia-gis.it/fossil/spatialite-tools/wiki?name=spatialite_osm_net).

Now, the network is inside the database, but we cannot make queries yet.
Let's open the spatialite console for the next operations :

    spatialite routing.sqlite

Spatialite's routing capabilities are provided through a *virtual* table. So we have to create it :

    CREATE VIRTUAL TABLE idf_net USING VirtualNetwork(net_data);
    
The previous command has loaded the network graph in memory, which means it is now availlable for our first query :

    SELECT * FROM idf_net WHERE NodeFrom = 123255457 AND NodeTo = 1430982681;

TODO : que deviennent les noeuds si on travaille sur une autre base ? Iti de Versailles au Louvre.

### Explore routing capabilities

This query provides the shortest path, but it is slow, because it uses the Dijkstra algorithm. 

With spatialite, we can specify that we want to use the `A*` algorithm, way faster, which give very good results on real networks.

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

What the fork ?

Regular SQL users are used to permanent modifications in table when we update them. But idf_net is not a table, it is a *virtual* table. 

This strange feature is here to provide a connection wide setting so that several concurent user can use whatever algorithm they want.
So the trick was to implement this surprsing column in memory... Which is not very consistant with SQL syntax.
Be carefull with automatic memory mangement, because if spatialite needs memory TODO : vérifier par une expérience ou la code, it will unload the virtual table, which will be recreated next time it is used... With the default algorithm (ie Dijstra)


## A note about Dijkstra and Astar

[Dijkstra algorithm](http://en.wikipedia.com/Dijkstra_(Algorithm)) TODO : vérifier le lien computes the shortest path between two nodes in a graph database where every connection has a positive cost (in our case, the cost is the length of the line)
The algorithm scans every node in order of increasing distance from the departure. Thus, it explores nodes in every direction. The algorithm stops when it finds the arrival node : no shortest path exists.

That's where Astar commes in action : this algorithms examines nodes preferentialy in the direction of the arrival and stops when it gets to it. This is far more faster ! But it offers no formal garanty that the result will be the shortest path. 
Here's how to trick it, for example :
TODO : dessin


## Creating a spatial index

Spatialite implements spatial index with `R*Tree` approche to speed up some queries, like finding the nearest node to start the route with.
So the final command we have to run in spatialite console.

    SELECT CreateSpatialIndex('roads', 'geometry');
    
This command creates a table `idx_roads_geometry` wich contains the id of each road and the bounding box. Section TODO describes how to take advantage of it.
