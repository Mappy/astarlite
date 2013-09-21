---
layout: default
title: Introduction
---
Introduction
=========


This tutorial tries to demonstrate the spatial capabilites of sqlite through the wonderfull spatialite module, which is a valid alternative to PostGIS if you don't need a client / server architecture.
We will run through the tools to deal with OpenStreetMap data, the manipulation of geographic features, the efficent use spatial index, and the not widely known routing algorithms.
TODO : typo d'OpenStreetMap

You will make a web application where you can click on a map to display the shortest path between two points and then change the route by draging the points.

You will find the final source of the whole project on [Github](http://www.github.com/jbernardes/astarlite), and a few example databases TODO here


* [Introduction](intro.html)
* [Install your environnement](install.html)
* [Prepare the data and discover spatialite](data.html)
* [Create a python routing server](server.html)
* [Display routes on the browser](client.html)
* [Conclusion](conclusion.html)

This tutorial, is a port of the very pedagogic [pgRouting workshop](http://workshop.pgrouting.com) for PostGIS from TODO. It TODO emphases on spatialite. Hence the html / javascript part will not be described.
