---
layout: default
---
# Compute route on the server

In this section, we will create a python service that returns a route in kml (a very common cartographic format for the web)

## Dependencies

If you don't already have Python, you can follow instructions on the main page : http://www.python.org/

We will use a web framework called bottle, which provides a web server, and an easy syntax 
to map function with an url (the `@route()` decorator), even with parameters. It also provides a templating syntax.
On Debian / ubuntu, you can install bottle with :

    sudo pip install bottle

## The main server

Here is a minimalist server, that will take as argument the path of the database we computed

 
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    from bottle import run
    import argparse

    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("database")
        args = parser.parse_args()
        print "Running server with database {}".format(args.database)
        run(host='localhost', port=8080, debug=True)


Run the server :

    python server.py ../routing.sqlite
    > Running server with database ../routing.sqlite

Now open in your browser the page [http://localhost:8000/](http://localhost:8000/)
You get an error 404, saying that this page is unknown... Because we have not declared 
any page in our server !

Let's add a handler to respond to a web query :

    from bottle import route, run, static_file, template
    
    @route('/route/<lat_from:float>,<lng_from:float>/<lat_to:float>,<lng_to:float>')
    def route(lat_from, lng_from, lat_to, lng_to):
        computed_path = "<LineString><coordinates>{},{} {},{}</coordinates></LineString>".format(
            lng_from,
            lat_from,
            lng_to,
            lat_to)
        return template("template.kml", path=computed_path)

The anotation `@route` exposes an url (the regexp in argument) on the server, and maps it with the following function. 
It allows the use of parameters in the url... You can even declare the type !

Note : the `@route` anotation (route as url routing) has nothing to do with function `def route():` (route as routing on a map).

The core of the function substitues the `path` parameter in the template  and returns it to the user (through http).
So we have to provide the template.kml file where the line will be inserted :

    <?xml version="1.0" encoding="utf-8" ?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document><Folder><name>Route</name>
      <Placemark>
        <Style><LineStyle><color>ff0000ff</color></LineStyle> 

                {% raw %} {{!path}} {% endraw %}
      
      </Placemark>
    </Folder></Document>
    </kml>

The quotation mark in `{% raw %} {{!path}} {% endraw %}` tells the template engine it not escape html characters (like opening tags).

Now let's try see [http://localhost:8000/route/48.85,3.35/48.90,2.40](http://localhost:8000/route/48.85,3.35/48.90,2.40) in your brower...

You can even watch it TODO : trouver un service
