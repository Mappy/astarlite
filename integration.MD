---
layout: default
---

# Display route on a map over the web
In this page, we will see how to display the kml we computed on web map. Once again, we will focus
on spatialite and a bit of Pyton. The html/js part is largely inspired from the pgRouting workshop (TODO). 

## Integrate html / javascript on the server

On the main server.py file, we will add two handlers :

    @route('/')
    def index():
        return template("index.html")

    @route('/js/<path:path>')
    def js(path):
        return static_file(path, root='js')

The first one will serve file index.html (TODO lien vers le code github), and the second one is
for javascript static files. You can store the library we use (etx, GeoExt, proj4js, OpenLayers) inside a `js` forlder on your project.




## Display the availlable area on the map
At startup, the map chould display area available for routing, so we will have to compute the bounding box that includes the roads.
The spatialite function `Extent()` is an aggregate, which means it returns one result for all the rows, exactly like the `max()` or the `count()` functions. 
Here, it computes a geomtry which is the bounding box of all geomtries from the table :

    SELECT Extent(geometry) FROM roads

Unfortunately, this does not give us directly the xmin, xmax, ymin and ymax values.

The extent is a Polygon geometry, and Polygons can have holes in spatialite. So we need extract what is called the exterior ring :

    SELECT ExteriorRing(Extent(geometry)) as linestring_bbox FROM roads;


The result is a Linestring geometry.

Now we can acces the points from the Linestring with the ''PointN()'' function, which indices are 1-based (instead of 0-based like arrays in many languages), and get the X() and the Y() values of these points :

    SELECT 
        X(PointN(linestring_bbox, 1)) as minx, 
        Y(PointN(linestring_bbox, 1)) as miny, 
        X(PointN(linestring_bbox, 3)) as maxx, 
        Y(PointN(linestring_bbox, 3)) as maxy 
        FROM (
            SELECT 
                ExteriorRing(Extent(geometry))as linestring_bbox 
            FROM roads
        )

We still have one more operation to do. OpenLayers, the javascript libray we use to display the route will display an OSM map. 
Unforunately this map will not accept coordinates in latitude and longitude, but in another coordinate system which is common in sofware maping : it has the same mercator look, but coordinates are in meters rather than in degrees of arc.
So we have to convert the bounding box from coordinate system (CS) 4326 to CS 3785.
In order to to that, we have to tell spatialite that our previous result has to be considered in CS 4326 with function ''SetSrid()'' and convert it with function ''ST_Transform()'' :

    SELECT 
        X(PointN(linestring_bbox, 1)) as minx, 
        Y(PointN(linestring_bbox, 1)) as miny, 
        X(PointN(linestring_bbox, 3)) as maxx, 
        Y(PointN(linestring_bbox, 3)) as maxy 
        FROM (
            SELECT ST_Transform(
                ExteriorRing(SetSrid(Extent(geometry), 4326)), 
              3785) as linestring_bbox FROM roads
        )

Here we are, at last !
