

import time
import BaseHTTPServer
import pprint
import cPickle as pickle
import cgi # for the "escape" function

import shared # event system shared code



HOST_NAME = 'services.taoriver.net'
PORT_NUMBER = 9010
WEBSERVER_URL = 'http://%s:%s/' % (HOST_NAME,PORT_NUMBER)

EVENTSERVER_HOST_NAME = 'services.taoriver.net'
EVENTSERVER_PORT_NUMBER = 9011
EVENTSERVER_URL = 'http://%s:%s/' % (EVENTSERVER_HOST_NAME,
                                     EVENTSERVER_PORT_NUMBER)

# import server
# LOGS_PICKLE = server.LOGS_PICKLE
# LOGS_PUBLIC = server.LOGS_PUBLIC -- not that you'd use this. (you'd just not run *period*..!
# MAX_LOGS_RETURNED = server.MAX_LOGS_RETURNED
LOGS_PICKLE = 'log.p'
MAX_LOGS_RETURNED = 50



root_page = """
<html>
  <head>
    <title>%(HOST_NAME)s:%(PORT_NUMBER)s - Event Server - Recent Logs</title>
  </head>
  <body>
    <p>
        Event server URL: http://%(EVENTSERVER_HOST_NAME)s:%(EVENTSERVER_PORT_NUMBER)s/
    </p>

    <p> Logs available here: </p>
    
    <ul>
    <li><a href="http://%(HOST_NAME)s:%(PORT_NUMBER)s/text/">text logs</a></li>
    <li><a href="http://%(HOST_NAME)s:%(PORT_NUMBER)s/html/">HTML logs</a></li>
    <li><a href="http://%(HOST_NAME)s:%(PORT_NUMBER)s/raw/">raw logs</a></li>
    </ul>
    
    <p>
        Here's how to post to it, manually:
    </p>

    <p>
    <code>
    <pre>
[lion@taoriver ~]$ python2.3
Python 2.3.2 (#1, Oct  6 2003, 10:07:16)
[GCC 3.2.2 20030222 (Red Hat Linux 3.2.2-5)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>>> import xmlrpclib
>>> s = xmlrpclib.ServerProxy( "http://%(EVENTSERVER_HOST_NAME)s:%(EVENTSERVER_PORT_NUMBER)s/" )
>>> s.notify( { "Action": "test", "Message": "Hello, world!" }, "password" )
1
>>>
    </pre>
    </code>
    </p>

    <p>
      To subscribe for event notice, you'll need to read some
      documentation on <a href="http://onebigsoup.wiki.taoriver.net/">the OneBigSoup wiki.</a>
      Sorry, I don't have time to write it up nicely just now.
    </p>
  </body>
</html>
""" % vars()



class ShowLogsHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def write_head(s, title ):
        s.wfile.write( "<html><head><title>" )
        s.wfile.write( HOST_NAME + ":" + str(PORT_NUMBER) + " - Event Server - %s" % title )
        s.wfile.write( "</title></head><body>" )
    def write_tail(s):
        s.wfile.write( "</body></html>" )

    def draw_raw(s):
        for log in s.logs():
            pprinted_text = pprint.pformat( shared.stripped_copy(log) )
            s.wfile.write( pprinted_text )
            s.wfile.write( "\n" )

    def draw_text(s):
        for log in s.logs():
            s.wfile.write( log.get( "TransparencyText",
                                    "(no self-description)" ) )
            s.wfile.write( "\n" )

    def draw_rss(s):
        s.wfile.write( """
<?xml version="1.0" encoding="ISO-8859-1" ?>
 <rss version="0.91">

 <channel>
 <title>%(HOST_NAME)s:%(PORT_NUMBER)s - Event Server - Recent Logs by RSS</title>
 <link>%(WEBSERVER_URL)s</link>
 <description>Event System Observation</description>
 <language>en-us</language>
        """ % globals() )
        for log in s.logs():
            s.wfile.write( "<item>" )
            s.wfile.write( "<title>%s</title>" %
                           log.get( "TransparencyText",
                                    "(no self-description)" ) )
            s.wfile.write( "<description>" )
            s.wfile.write( cgi.escape(pprint.pformat(shared.stripped_copy(log))) )
            s.wfile.write( "</description>" )
            s.wfile.write( "</item>" )
        s.wfile.write( "</channel>" )
        s.wfile.write( "</rss>" )

    def draw_html(s):
        s.write_head( "HTML logs" )
        
        in_table = 0
        current_headers = None
        
        for log in s.logs():
            if log.has_key( "TransparencyXhtmlColumnHeaders" ) and log.has_key( "TransparencyXhtmlRow" ):
                if current_headers != log["TransparencyXhtmlColumnHeaders"]:
                    current_headers = log["TransparencyXhtmlColumnHeaders"]
                    escaped_headers = []
                    for header in current_headers:
                        escaped_headers.append( cgi.escape(header) )
                    if not in_table:
                        s.wfile.write( "<table>" )
                    else:
                        s.wfile.write( "</table><table>" )
                    in_table = 1
                    s.wfile.write( "<tr><td><b>" + "</td><td><b>".join( escaped_headers ) + "</b></tr>" )
                s.wfile.write( "<tr><td>" + "</td><td>".join( log["TransparencyXhtmlRow"] ) )
            else:
                if in_table:
                    if current_headers != None:
                        s.wfile.write( "</table><table>" )
                        current_headers = None
                else:
                    s.wfile.write( "<table>" )
                    in_table = 1
                    current_headers = None
                if log.has_key( "TransparencyXhtml" ):
                    s.wfile.write( "<tr><td>%s</td></tr>" % log["TransparencyXhtml"] )
                elif log.has_key( "TransparencyText" ):
                    s.wfile.write( "<tr><td>%s</td></tr>" % cgi.escape(log["TransparencyText"]) )
                else:
                    s.wfile.write( "<tr><td>(no self-description)</td></tr>" )
        if in_table == 1:
            s.wfile.write( "</table>" )
        s.write_tail()

    def content_type(s):
        if s.path in ["/text/", "/raw/"]:
            return "text/plain"
        return "text/html"
        
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", s.content_type())
        s.end_headers()
    def do_GET(s):
        """Serve a GET request."""
        s.send_response(200)
        s.send_header("Content-type", s.content_type())
        s.end_headers()
        if s.path == "/":
            s.wfile.write( root_page )
        elif s.path == "/text/":
            s.draw_text()
        elif s.path == "/html/":
            s.draw_html()
        elif s.path == "/raw/":
            s.draw_raw()
        elif s.path == "/rss/":
            s.draw_rss()
        else:
            s.wfile.write( root_page )

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
