

import time
import BaseHTTPServer
import pprint
import cPickle as pickle



HOST_NAME = 'services.taoriver.net'
PORT_NUMBER = 9010

# import server
# LOGS_PICKLE = server.LOGS_PICKLE
# LOGS_PUBLIC = server.LOGS_PUBLIC -- not that you'd use this. (you'd just not run *period*..!
# MAX_LOGS_RETURNED = server.MAX_LOGS_RETURNED
LOGS_PICKLE = 'log.p'
MAX_LOGS_RETURNED = 50


class ShowLogsHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Serve a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write( "<html><head><title>" )
        s.wfile.write( HOST_NAME + ":" + str(PORT_NUMBER) + " - Event Server - Recent Logs" )
        s.wfile.write( "</title></head><body>" )
        for log in s.logs():
            s.wfile.write( "<tr><td><pre>")
            s.wfile.write( pprint.pformat( log ) )
            s.wfile.write( "</pre></td></tr>" )
        s.wfile.write( "</body>" )
    def logs(s):
        try:
            log = pickle.load( open( LOGS_PICKLE, "r" ) )
        except IOError:
            log = []
        return log

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class( (HOST_NAME, PORT_NUMBER),
                          ShowLogsHandler )
    print time.asctime(), "TransparentMessaging Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.close() # might work..?
    print time.asctime(), "TransparentMessaging Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
