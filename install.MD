---
layout: default
---
# Installing you environnement

You are strongly encouraged you to work on Linux, which has been proved to work well. On other plateform, you can use a virtual machine, like the OSGeo Live (TODO : version + lien + vérifier que ça marche)

If you successfuly installed the application or the tools on another plateform, please submit a pull request to improve this tutorial, or simply let <a href="mailto:astarlite@lexman.org">us know !</a>

## On Ubuntu
    sudo apt-get install sqlite3 libspatialite3 spatialite3 python-pysqlite2 spatialite-binspatialite-gui

## On Windows
### Server dependencies
One can try to install binaries from [http://www.gaia-gis.it/gaia-sins/](http://www.gaia-gis.it/gaia-sins/) under MS Windows binaries section. Consider using a virtual machine .
TODO : tester si on peut au moins installer le serveur (tant pis pour les outils de génération de données)
### Data preparation

## On Mac OSX
MacPorts are too old (spatialite version is 2.3.1), compiling libspatialite is not straightforward (since you need proj4 and geos). Consider using a [virtual machine](#virtualmachin).

## Using a Virtual Machine
TODO : ancres html

[Download](http://live.osgeo.org/en/download.html) a virtual machine and follow the instructions from [OSGeoLive](http://live.osgeo.org/en/quickstart/virtualization_quickstart.html)
This distributions already contains python, the spatialite libraries and spatialite OSM tools.

