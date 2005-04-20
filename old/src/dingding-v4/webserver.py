

import time
import BaseHTTPServer
import pprint
import cPickle as pickle
import cgi # for the "escape" function

import shared # event system shared code
import log_display



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



html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;" }

def html_escape( text ):
    l=[]
    for c in text:
        l.append( html_escape_table.get(c,c) )
    return "".join(l)



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
    <li><a href="http://%(HOST_NAME)s:%(PORT_NUMBER)s/rss/">rss 0.91 logs</a></li>
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

    def draw_rss(s):
        sorted_logs = log_display.sort_logs( s.logs() )
        title = "%(HOST_NAME)s:%(PORT_NUMBER)s - Event Server - Recent Logs by RSS" % globals()
        link = WEBSERVER_URL
        description = "Event System Observation"
        language = "en-us"
        
        code = log_display.as_rss( sorted_logs,
                                   title,
                                   link,
                                   description,
                                   language )
        
        s.wfile.write( code )

    def content_type(s):
        if s.path in ["/text/", "/raw/"]:
            return "text/plain"
        if s.path == "/rss/":
            return "application/rss+xml"
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
            return
        if s.path == "/rss/":
            s.draw_rss()
            return
        
        sorted_logs = log_display.sort_logs(s.logs())
        stripped = []
        for log in sorted_logs:
            stripped.append( shared.stripped_copy(log) )
        sorted_logs = stripped
        
        if s.path == "/text/":
            output = log_display.as_text( sorted_logs )
        elif s.path == "/html/":
            output = log_display.as_html( sorted_logs )
        elif s.path == "/raw/":
            output = log_display.as_raw( sorted_logs )
        else:
            output = root_page
            
        if s.path == "/html/":
            s.write_head( "HTML Log" )
        s.wfile.write( output )
        if s.path == "/html/":
            s.write_tail()

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
