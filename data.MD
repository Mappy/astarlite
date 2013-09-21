---
layout: default
title: 
---
# Explore spatialite and create pre-processed database

## A word about spatialite
We are about to build a spatialite database for routing. [Spatialite](http://www.gaia-gis.it/gaia-sins/) TODO vérifier le lien is an extension for the [sqlite](bla) TODO : lien database.
Sqlite is not a common database in the sense that we are used to client-server databases like Postgresql or MySQL. Sqlite works as a library you use into your application, which produces local files (eg routing.sqlite). 
No need to install a server, deploying the application is suffisent. The only downside is that the spatialite extension to sqlite is not trivial to install on some plateforms because of the numerous dependencies.


## Create the database
### Download OSM data

You can download OpenStreeMap data from [Cloudmade](http://downloads.cloudmade.com) which gracefully give access to several areas.

We'll work on the suburban area around Paris called Île-de-France. You can download the ile-de-france.osm.bz2 file on [http://downloads.cloudmade.com/europe/western_europe/france/ile-de-france#downloads_breadcrumbs](http://downloads.cloudmade.com/europe/western_europe/france/ile-de-france#downloads_breadcrumbs).
If you want faster computations, you can use a smaller data set such as the very small country called Monaco.

### Create the routing enabled database
In order to setup a database that is suitable for routing computation, you need to decompress ile-de-france.osm.bz2 (you will need 20 Go TODO vérifier of free disk space)

    bunzip2 ile-de-france.osm.bz2

We will insert all the roads in the database with the spatialite_osm_net command line utility, part of the spatialite-tools we installed from spatialite-bin package.

    spatialite_osm_net -o  ile-de-france.osm -d routing.sqlite -T roads -m

That was not so long ! 

Prepare to wait much longer for the next command : 
creation of the network with the internal data structure suitable for routing algorithms.

    spatialite_network --db-path routing.sqlite --table roads --from-column node_from --to-column node_to --geometry-column geometry --a-star-supported  --name-column name --bidirectional --output-table net_data

More options are avalables to generate an oriented graph, to specify a specific cost for each arc (by default, we use the length of the geometry).
You can also use the spatialite-gui tool as described on the [spatialite wiki](https://www.gaia-gis.it/fossil/spatialite-tools/wiki?name=spatialite_osm_net).

Now, the network is inside the database, but we cannot make queries yet.
Let's open the spatialite console for the next operations :

    spatialite routing.sqlite

Instead of providing an SQL function, spatialite's interface to routing capabilities are *virtual* tables. So we have to create it :

    CREATE VIRTUAL TABLE idf_net USING VirtualNetwork(net_data);
    
The previous command has loaded the network graph in memory, which means it is now availlable for making ou first query :

    SELECT * FROM idf_net WHERE NodeFrom = 123255457 AND NodeTo = 1430982681;

TODO : que deviennent les noeuds si on travaille sur une autre base ?

### Explore routing capabilities

This query might be slow, because it uses the Dijkstra algorithm, which will stricty provide the shortest path.

We can specify that we want to use the A* algorithm, way faster, which give very good results on real networks.

    UPDATE idf_net SET Algorithm = "A*";
    
We can see duration of the queries in the spatialite console by enbabling time measurment

    .timer ON
And make our query again

    SELECT * FROM idf_net WHERE NodeFrom = 123255457 AND NodeTo = 1430982681;
     
Now the processing time is reasonable !
    

### A note about Dijkstra and Astar

[Dijkstra algorithm](http://en.wikipedia.com/Dijkstra_(Algorithm)) TODO : vérifier le lien computes the shortest path between two nodes in a graph database. It scans every node, going away from the departure in every direction. There will be a moment when the algorithms scans the arrival node. It keeps on scanning nodes, in case the would be a shorter route through an unexplored node yet. It stops when TODO.
. In order to do that, it has to examine every 
Thus, the algorithm examines many nodes from the graph, which is really time consuming. Do we really have to examine node in Russia if we are trying to compute a route between Paris and Berlin ?

That's where Astar commes in action : this algorithms examines nodes preferentialy in the direction of the arrival and stops when it gets to it. This is far more faster ! But it offers no formal garanty that this will be the shortest path. 
Here's how to trick it, or example :
TODO : dessin

