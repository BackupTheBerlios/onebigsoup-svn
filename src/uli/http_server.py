"""
Generic Python2.3 HTTP+ULI server.

Fields ULI calls and GET requests, so that anybody can use it.

(c) 2004 Lion Kimbro, and dedicated into the Public Domain.

  You can do ANYTHING that you want with this.
  You can re-license your copy however you like.

  IF YOU CHANGE IT, though,
  fix the name to *your* name, and update the year.

  I don't like proprietary licenses.
  I request, but do not require,
    that this not be used in proprietary software.
  In particular, I request, but do not require,
    that Microsoft not use this software in their own.
"""

import time
import BaseHTTPServer
import sys
import cgi
import pprint

# In the event get_func is not defined,
# (that is, this has no ULI definition,)
# then this is the message that is given
# to the user.

THIS_IS_JUST_ULI = """
<html><head><title>ULI-only</title></head></body>
<p>
This web server exists only for <a href="http://onebigsoup.wiki.taoriver.net/moin.cgi/UniversalLineInterface">Universal Line Interface</a> interactions.
</p>

<p>
Please communicate with the wiki by HTTP-POST-ULI.
</p>
</body></html>
"""

THERE_IS_NO_ULI = "This server, sadly, does not support ULI interactions."

class UliHttpHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def path_as_list():
        not_blank = lambda x:x!=""
        path = filter( not_blank, s.path.split("/") )
        return path
    
    def do_HEAD(s):
        print "do_HEAD"
        if s.server.redirect_func == None:
            goto = None
        else:
            try:
                goto = s.server.redirect_func( s.path_as_list() ) # CAN return None
            except:
                e = sys.exc_info()[1]
                print "ERROR WHILE PROCESSING PATH:", s.path
                print e
                s.send_response(404)
                s.end_headers()
                return
        
        if goto == None:
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
        else:
            s.send_response(301)
            s.send_header( "Location", result )
            s.end_headers()

    def do_GET(s):
        print "do_GET"
        s.do_HEAD()

        if s.server.get_func != None:
            msg = s.server.get_func( s.path_as_list() )
        else:
            msg = THIS_IS_JUST_ULI

        s.wfile.write( msg )
        
    def do_POST(s):
        print "do_POST"
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

        if s.server.uli_func != None:
            msg = s.server.uli_func( uli_string )
        else:
            msg = THERE_IS_NO_ULI

        s.wfile.write( msg )

class UliHttpServer( BaseHTTPServer.HTTPServer ):
    def __init__( s, server_addr,
                  redirect_func=None, get_func=None, uli_func=None ):
        """
        server_addr: tuple, of the form (HOST_NAME, PORT_NUMBER)
          ex: ("services.taoriver.net",9300)
        
        uli_func( line )   --> returns ULI response line
        get_func( path )   --> returns web page text
        redirect_func( path ) --> returns target URL or None
          (None if there is no redirection to perform.)

        line: string line
        
        path: always a list
          http://taoriver.net/one/big/soup
        ...would be...
          ["one","big","soup"]
        ...by the time it hits get_func or redirect_func
        """
        print server_addr, UliHttpServer
        BaseHTTPServer.HTTPServer.__init__( s, server_addr, UliHttpHandler )
        
        s.redirect_func = redirect_func
        s.get_func = get_func
        s.uli_func = uli_func

if __name__ == '__main__':
    HOST_NAME = 'services.taoriver.net' # !!!REMEMBER TO CHANGE THIS!!!
    PORT_NUMBER = 9300

    httpd = UliHttpServer( (HOST_NAME,PORT_NUMBER) )
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)


