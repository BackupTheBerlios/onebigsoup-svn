#!/usr/bin/python2.3
"""
Python2.3 Local Names 1.1 server

"""

import BaseHTTPServer
import cgi
import xmlrpclib
import xml.parsers.expat

import localnames


class LocalNamesHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """
    Handles GET, POST, and interprets ULI, GTF, XML-RPC.
    """
    
    def do_GET(self):
        self.send_response(301)
        self.send_header("Location", "http://slashdot.org/")
        self.end_headers()

    def do_POST(self):
        clen = int(self.headers.getheader("content-length"))
        body = self.rfile.read(clen)
        try:
            call_data = xmlrpclib.loads(body)
        except xml.parsers.expat.ExpatError:
            call_data = None
        # d = cgi.parse_qs(body) -- for later
        # -- for now, assuming always XML-RPC
        (args, funct) = call_data
        if funct == "filterData":
            result = self.filterData(args[0], args[1], args[2])
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(xmlrpclib.dumps((result,)))

    def filterData(self, data, contentType, params):
        data = data.decode("utf-8", "replace")
        url = params["namespace"]
        return localnames.replace_text(data, url)


if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(("localhost", 9000), LocalNamesHandler)
    httpd.serve_forever()

