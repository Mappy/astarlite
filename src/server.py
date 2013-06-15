#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, static_file, template
from spatialite_routing import Routing
import argparse

routing = None

@route('/')
def index():
    center = routing.get_center()
    return template("index.html", center_x = center[0], center_y = center[1])

@route('/js/<path:path>')
def js(path):
    return static_file(path, root='js')

@route('/route/<start>/<end>')
def route(start, end):
    lat_from, lng_from = tuple(map(float, start.split(",")))
    lat_to, lng_to = tuple(map(float, end.split(",")))
    path = routing.compute_route(lat_from, lng_from, lat_to, lng_to)
    return template("template.kml", path=path)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    args = parser.parse_args()
    routing = Routing(args.database)
    run(host='localhost', port=8080, debug=True)
