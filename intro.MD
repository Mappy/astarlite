---
layout: default
title: Introduction
---
Introduction
=========


The purpose of this tutorial is to demonstrate the spatial capabilites of sqlite through the wonderfull spatialite module, which is a valid alternative to PostGIS if you don't need a client / server architecture.
We will run through the tools to deal with OpenStreetMap data, the manipulation of geographic features, the efficent use spatial index, and a not widely known features... Routing algorithms !

You will make a web application where you can click on a map to display the shortest path between two points and then modify the route by draging the points.

You will find the final source of the whole project on [Github](http://www.github.com/mappy/astarlite), and a few example databases TODO [here](http://mappy.github.com/astarlite-assets)

* [Install your environnement](install.html)
* [Prepare the data and discover spatialite](data.html)
* [Create a python server](server.html)
* [Compute routes on the server](spatialite.html)
* [Display routes on the browser](client.html)
* [Integrate the client side into the server](integration.html)
* [Random considerations](considerations.html)
* [Conclusion](conclusion.html)

This tutorial, is a port of the very pedagogic [pgRouting workshop](http://workshop.pgrouting.com) for PostGIS from Daniel Kastl and Frédéric Junod. It is aimed at emphasing spatialite capabilities. Hence the html / javascript part will is a copy from the former [pgRouting 1.05 workshop](http://postgis.fr/chrome/site/docs/workshop-routing-foss4g/docs/_build/html/chapters/geoext_client.html).
