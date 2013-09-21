---
layout: default
title: Explore spatialite and pre-process a database
---
# 

## Download data

You can download OpenStreeMap data from Cloudmade which gracefully give access to several zones.

We'll work on the suburban area around Paris called Île-de-France. You can download the ile-de-france.osm.bz2 file on http://downloads.cloudmade.com/europe/western_europe/france/ile-de-france#downloads_breadcrumbs using download_data.sh
(If you want faster results, you can use a smaller data set such as Monaco)

## Create the routing enabled database
Now, we'll set a database that is suitable for routing computation.

If you have not used download_data.sh, you need to decompress ile-de-france.osm.bz2

    bunzip2 ile-de-france.osm.bz2

We need to insert all the roads in the database thanks to the spatialite_osm_net command line interface, part of the spatialite-tools utilities, installed from spatialite-bin Ubuntu package.

    spatialite_osm_net -o  ile-de-france.osm -d routing.sqlite -T roads -m

The previous line has created a database file.  

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
    
