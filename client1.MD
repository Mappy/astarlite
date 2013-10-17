---
layout: default
---
# Display routes on the client browser

## Display a basic map
[GeoExt](http://www.geoext.org) is a JavaScript Toolkit for Rich Web Mapping Applications. GeoExt brings together the geospatial know how of [OpenLayers](http://www.openlayers.org) with the user interface savvy of [Ext JS](http://www.sencha.com) to help you build powerful desktop style GIS apps on the web with JavaScript.

Let’s start with a simple GeoExt example and extend it with routing functionality then:

    <html>
    <head>

    <title>A Basic GeoExt Page</title>
    <script src="ext/adapter/ext/ext-base.js" type="text/javascript"></script>
    <script src="ext/ext-all.js"  type="text/javascript"></script>
    <link rel="stylesheet" type="text/css" href="ext/resources/css/ext-all.css" />
    <script src="OpenLayers/OpenLayers.js" type="text/javascript"></script>
    <script src="GeoExt/script/GeoExt.js" type="text/javascript"></script>
    <link rel="stylesheet" type="text/css"
          href="GeoExt/resources/css/geoext-all.css" />

    <script type="text/javascript">
        Ext.onReady(function() {
            var panel = new GeoExt.MapPanel({
                renderTo: 'gxmap',
                map: {
                    layers: [new OpenLayers.Layer.OSM("Simple OSM Map")]
                },
                zoom: 1,
                height: 400,
                width: 600,
                title: 'A map for routing'
            });
        });
    </script>
    </head>
    <body>
    <div id="gxmap"></div>
    </body>
    </html>


In the header we include all the javascript and css needed for the application, we also define a function to be run when the page is loaded (Ext.onReady).

This function creates a GeoExt.MapPanel with an OpenStreetMap layer. In this code, no OpenLayers.Map is explicitly created; the GeoExt.MapPanel do this under the hood: it takes the map options, the center and the zoom and create a map instance accordingly.

To allow our users to get directions, we need to provide a way to select the start and final destination.


## Select the start and final destination

We want to allow the users to draw and move the start and final destination points by clicking the map. 
The browser queries the server and displays the route on the map. The user can later move the start 
or final point and the route is updated.

To do this we will need a tool to draw points (we will use the OpenLayers.Control.DrawFeatures control) and a tool to
move points (OpenLayers.Control.DragFeatures will be perfect for this job). As their name suggests these
controls comes from OpenLayers.

These two controls will need a place to draw and manipulate the points; we will also need an 
OpenLayers.Layer.Vector layer. In OpenLayers, a vector layer is a place where features
(a geometry and attributes) can be drawn programmatically (in contrast, the OSM layer is a raster layer).


Create the layer where the start and final points will be drawn and add it to the map :
    var points_layer = new OpenLayers.Layer.Vector("points");
    map.addLayers([points_layer, route_layer]);


Let’s look at the control to draw the points: because this component has special behavior it’s more easy to 
create a new class based on the standard OpenLayers.Control.DrawFeatures control. This new control 
(named DrawPoints) is saved in a separated javascript file (web/DrawPoints.js):

DrawPoints = OpenLayers.Class(OpenLayers.Control.DrawFeature, {

    // this control is active by default
    autoActivate: true,

    initialize: function(layer, options) {
        // only points can be drawn
        var handler = OpenLayers.Handler.Point;
        OpenLayers.Control.DrawFeature.prototype.initialize.apply(
				this, [layer, handler, options]
			);
    },

    drawFeature: function(geometry) {
        OpenLayers.Control.DrawFeature.prototype.drawFeature.apply(
				this, arguments	
			);
        if (this.layer.features.length == 1) {
            // we just draw the startpoint
            // note: if we want to apply a special style to the 
            //       start point we should do this here
        } else if (this.layer.features.length == 2) {
            // we just draw the finalpoint
            // note: if we want to apply a special style to the 
            //       final point we should do this here

            // we have all what we need; we can deactivate ourself.
            this.deactivate();            
        }
    }
});


In the initialize function (that’s the class constructor) we set that this control can only draw 
points (handler variable is OpenLayers.Handler.Point).

The special behavior is implemented in the drawFeature function: because we only need the start and 
final points the control deactivates itself when two points are drawn by counting how many features
has the vector layer. Control deactivation is this.deactivate().

Our control is then created with:

    // create the control to draw the points (see the DrawPoints.js file)
    var draw_points = new DrawPoints(points_layer);
points_layer is the vector layer created earlier.


And now for the DragFeature control:

    // create the control to move the points
    var drag_points = new OpenLayers.Control.DragFeature(points_layer, {
        autoActivate: true
    });
Again, `points_layer` is the vector layer, `autoActivate: true` tells OpenLayers that we want this 
control to be automatically activated.

    // add the controls to the map
    map.addControls([draw_points, drag_points]);
Adds the controls to the map.

## Call and receive data from web service

The basic workflow to get a route from the web server is:

* transform our points coordinates from EPSG:900913 (native coordinates for a OpenStreetMap in OpenLayers) to EPSG:4326 (latitude and longitude)
* call the web service with the coordinnates of both points
* add the response to the map in a Kml vector layer

The first item is something new: our map uses the EPSG:900913 projection (because we use an OSM layer) but the web service expects coordinates 
in EPSG:4326: we have to re-project the data before sending them. This is not a big deal: we will 
simply use the Proj4js javascript library.

**(The second item call the web service is covered in the next paragraph.)**


## Trigger the web service call
We need to call the web service when:
* the two points are drawn
* one of the point is moved
Our vector layer generates an event (called featureadded) when a new feature is added, we can listen to 
this event and call the server routing function:

    draw_layer.events.on({
        featureadded: function() {
            query_route(draw_layer);
        }
    });
Note Before we continue some words about events: an event in OpenLayers (the same apply for ExtJS and 
other frameworks), is a system to allow a function to be called when something happened. For instance 
when a layer is added to the map or when the mouse is over a feature. Multiple functions can be 
connected to the same event.
No event is generated when a point is moved, hopefully we can give a function to the DragFeature
control to be called we the point is moved:

    drag_points.onComplete = function() {
        query_route(draw_layer);
    };
It's time to present the `query_route` function :

     function query_route(layer) {
         if (layer.features.length == 2) {
             // erase the previous route
             if (kml_layer != null) {				 
				map.removeLayer(kml_layer);
 			 }

             // transform the two geometries from EPSG:900913 to EPSG:4326
             var startpoint = layer.features[0].geometry.clone();
             startpoint.transform(epsg_900913, epsg_4326);
             var finalpoint = layer.features[1].geometry.clone();
             finalpoint.transform(epsg_900913, epsg_4326);

             // load to route             
			 url = "/route/" + startpoint.y + "," + startpoint.x + "/" + finalpoint.y + "," + finalpoint.x;
			 kml_layer = new OpenLayers.Layer.Vector("KML", {
				 strategies : [new OpenLayers.Strategy.Fixed()],
				 protocol : new OpenLayers.Protocol.HTTP({
					 url : url,
					 format : new OpenLayers.Format.KML({
						 extractStyles : true,
						 extractAttributes : true,
						 maxDepth : 2
					 })
				 })
			 });
			 map.addLayers([kml_layer]);
         }
    }

At first, the function checks that the layer in argument contains two points. Then, `map.removeLayer(kml_layer);` is called to ensure any previous result is disposed. 
Then both start and end points coordinates are projected using OpenLayers.Projection instances.

Finally, we construct a kml vector layer that will receive the result of the routing query passed to the server with coordinates as arguments.
