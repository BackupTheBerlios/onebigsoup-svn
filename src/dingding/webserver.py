

import time
import BaseHTTPServer
import pprint
import cPickle as pickle

import shared # event system shared code



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
        s.wfile.write( """
<p>
  Here's how to post to the event server, which is running on: http://services.taoriver.net:9011/
</p>

<p>
<code>
<pre>
[lion@taoriver ~]$ python2.3
Python 2.3.2 (#1, Oct  6 2003, 10:07:16)
[GCC 3.2.2 20030222 (Red Hat Linux 3.2.2-5)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>>> import xmlrpclib
>>> s = xmlrpclib.ServerProxy( "http://services.taoriver.net:9011/" )
>>> s.notify( { "Action": "test", "Message": "Hello, world!" }, "password" )
1
>>> 
</pre>
</code>
</p>

<p>
  To subscribe, you'll need to read some documentation on <a href="http://onebigsoup.wiki.taoriver.net/">the OneBigSoup wiki.</a>
</p>

<p>
  Sorry, don't have time to locate it right now.
</p>
        """)
        for log in s.logs():
            s.wfile.write( "<tr><td><pre>")
            s.wfile.write( pprint.pformat( shared.stripped_copy(log) ) )
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
