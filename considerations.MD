---
layout: default
---
#Further considerations

## Query time
On my Atom notebook, a query over Ile-De-France is about 200 ms, which is quite fast ! 

## Memory
creates data for propagation as the algorithm runs

## Load
When the algorithm runs concurently (because two users make queries), 
the graph data is shared, so only the memory for runing the algorithm is necessary
~ Ok

## Change
* Won't take changes into effect unless spatialite_network

## Data quality
https://www.gaia-gis.it/fossil/spatialite-tools/wiki?name=graphs-intro

## Differences with pgRouting
* not as rich functionnally
* changes are not taken into account
* faster and more efficent in a load context

## Going further
* algorithm very sensitive to the quality of input data. OSM ~ cf explaination in spatialite's site
* Example is for pedestrians, doesn't take into accout one ways, but the graph can be built both ways
