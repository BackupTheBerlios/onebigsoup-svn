"""
HTTP ULI - XML-RPC ULI gateway

Forwards HTTP ULI requests to an XML-RPC ULI server.
"""

import BaseHTTPServer
import xmlrpclib
import time
import sys
import cgi
import pprint


HOST_NAME = 'services.taoriver.net' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 9095 # Maybe set this to 80
XMLRPC_TARGET = "http://services.taoriver.net:9090/"


class MyHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.do_HEAD()
        s.wfile.write( "<html><head><title>Done!</title></head><body>" )
        s.wfile.write( "<p>Done!</p>" )
        s.wfile.write( "</body></html>" )
    def do_POST(s):
        s.do_HEAD()
        clen = int( s.headers.getheader("content-length") )
        body = s.rfile.read( clen )
        print "-----  POST  ------"
        print time.asctime()
        print "path:", s.path
        print "content-length", clen
        print "---- CONTENT ------"
        print body
        print "---- DECODED ------"
        d = cgi.parse_qs( body )
        pprint.pprint(d)
        print "--- ULI DECODED ---"
        try:
            uli_string = d.get("ULI",d.get("uli",d.get("Uli","(NO ULI PARAMETER!)")))[0]
        except KeyError:
            uli_string = "(NO ULI PARAMETER - can't figure out how to decode input)"
        print ">>>", uli_string
        print "-------------------"
        server = xmlrpclib.ServerProxy( XMLRPC_TARGET )
        s.wfile.write( server.uli( uli_string ) )
        

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class( (HOST_NAME, PORT_NUMBER),
                          MyHandler )
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)


