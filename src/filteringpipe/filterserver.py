#!/usr/bin/python2.3
"""
Python2.3 Filters Server

Servers Markdown, SmartyPants, and whatever else we decide to throw in here.

"""

import BaseHTTPServer
import cgi
import xmlrpclib
import xml.parsers.expat

import pymarkdown


class FiltersHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """Handles GET, POST, and interprets ULI, GTF, XML-RPC."""

    def do_POST(self):
        clen = int(self.headers.getheader("content-length"))
        body = self.rfile.read(clen)
        try:
            (args, funct) = xmlrpclib.loads(body)
        except xml.parsers.expat.ExpatError:
            (args, funct) = (None, None)
        print funct
        print args
        if funct in ["filterData", "wiki.filterData"]:
            if self.path.lower() == "/markdown/":
                result = self.xmlrpc_markdown(*args)
            else:
                result = "the path URL tells what filter to use: ex: http://services.taoriver.net:9001/markdown/"
            self.send_response(200)
            self.send_header(u'Content-type', u'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(xmlrpclib.dumps((result,)))
            return
        self.wfile.write(xmlrpclib.dumps(("call either filterData or wiki.filterData",)))

    def xmlrpc_markdown(self, data, contentType, params):
        data = str(data)
        data = data.decode("utf-8", "replace")
        data = pymarkdown.Markdown(data)
        data = data.encode("utf-8", "replace")
        data = xmlrpclib.Binary(data)
        return {"data": data, "contentType": contentType}


if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(("localhost", 9001), FiltersHandler)
    httpd.serve_forever()

