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

Windows spatialite windows are available at http://www.gaia-gis.it/gaia-sins/windows-bin-x86/ . At the time of writing, spatialite is in version 4.2 and has been tested under Windows 8.1.
You need to download and unzip : spatialite_network.exe, spatialite_osm_net.exe and spatialite.exe to precompute the data.

You'll also have to unzip mod_spatialite-4.2.0-win-x86 to get the DLL of the extension in the same directory as your python server code, so the library is loadable.

### Data preparation

## On Mac OSX
MacPorts are too old (spatialite version is 2.3.1), compiling libspatialite is not straightforward (since you need proj4 and geos). Consider using a [virtual machine](#virtualmachin).

## Using a Virtual Machine

[Download](http://live.osgeo.org/en/download.html) a virtual machine and follow the instructions from [OSGeoLive](http://live.osgeo.org/en/quickstart/virtualization_quickstart.html)
This distributions already contains python, the spatialite libraries and spatialite OSM tools.

