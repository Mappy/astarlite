---
layout: default
---
# Installing you environnement

You are strongly encouraged you to work on Linux, which has been proved to work well. On other plateform, you can use a virtual machine, like the OSGeo Live (TODO : version + lien + vérifier que ça marche)
If you successfuly installed it on another plateform, please submit a pull request to improve this tutorial, or simply let <a href="mailto:astarlite@lexman.org">us know !</a>

## On Ubuntu
    sudo apt-get install sqlite3 libspatialite3 spatialite3 python-pysqlite2 spatialite-binspatialite-gui

## On Windows
One can try to install binaries from http://www.gaia-gis.it/gaia-sins/ under MS Windows binaries section. Consider using a [virtual machine](#virtualmachin).
TODO : tester si on peut au moins installer le serveur (tant pis pour les outils de génération de données)

## On Mac OSX
MacPorts are too old (spatialite version is 2.3.1), compiling libspatialite is not straightforward (since you need proj4 and geos). Consider using a [virtual machine](#virtualmachin).

## <a id="virtualmachine"></a>Using a Virtual Machine
TODO : ancres html
Go to http://live.osgeo.org/en/download.html, download a virtual machine and follow the instructions here http://live.osgeo.org/en/quickstart/virtualization_quickstart.html
This distributions already contains libspatialite3 spatialite-bin

