astarlite
=========


## Get the data

You can get OpenStreeMap data on your working area on Cloudmade which gracefully give access to several zones.

We'll work on the surburban area around Paris called Île-de-France. You can download the ile-de-france.osm.bz2 file on http://downloads.cloudmade.com/europe/western_europe/france/ile-de-france#downloads_breadcrumbs


## Install the dependencies

### On Ubuntu
    apt-get install libspatialite3 spatialite-bin

### On Windows



## Prepare the data
Now, we'll set a database that is suitable for routing computation.

First decompress the data ile-de-france.osm.bz2


First, we need to insert all the roads in the database thanks to the spatialite_osm_net command line interface, part of the spatialite-tools utilities, installed from spatialite-bin Ubuntu package.

spatialite_osm_net -o  ile-de-france.osm -routing.sqlite -T roads -m
