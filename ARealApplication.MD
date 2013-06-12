# A real Application

We'll make a web application in Python / javascript that let you point to compute routing

If you don't already have Python, you can follow instructions on the main page : http://www.python.org/

## The html web page
GeoExt is a JavaScript Toolkit for Rich Web Mapping Applications. GeoExt brings together the geospatial know how of OpenLayers with the user interface savvy of Ext JS to help you build powerful desktop style GIS apps on the web with JavaScript.

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
            center: [-11685000, 4827000],
            zoom: 12,
            height: 400,
            width: 600,
            title: 'A Simple GeoExt Map'
        });
    });
</script>
</head>
<body>
<div id="gxmap"></div>
</body>
</html>
