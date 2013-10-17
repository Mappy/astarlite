#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, static_file, template
from spatialite_routing import Routing
import argparse

routing = None

@route('/')
def index():
    extent = routing.get_extent()
    return template("index.html", extent)

@route('/js/<path:path>')
def js(path):
    return static_file(path, root='js')

@route('/route/<lat_from:float>,<lng_from:float>/<lat_to:float>,<lng_to:float>')
def route(lat_from, lng_from, lat_to, lng_to):
    path = routing.compute_route(lat_from, lng_from, lat_to, lng_to)
    return template("template.kml", path=path)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    args = parser.parse_args()
    routing = Routing(args.database)
    print "Running server with database {}".format(args.database)
    run(host='localhost', port=8080, debug=True)
