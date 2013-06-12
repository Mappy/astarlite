#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, static_file

@route('/')
def index():
    return static_file("index.html", root=".")

@route('/js/<path:path>')
def js(path):
    return static_file(path, root='js')

@route('/hello')
def hello():
    return "Everyday a star is born (Can you say New York City?) Clap for 'em, clap for 'em, clap for 'em, hey"

run(host='localhost', port=8080, debug=True)
