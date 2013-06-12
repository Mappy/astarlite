#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SimpleHTTPServer
import SocketServer

class AStarLiteRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def __init__(request, client_address, server):
		SimpleHTTPServer.SimpleHTTPRequestHandler(self, request, client_address, server)
		pass

	def do_GET(self):
		print '***', self.path

PORT = 8000

Handler = AStarLiteRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()