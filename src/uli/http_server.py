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
<html><head><title>%(name)s</title></head></body>
<h3>%(name)s</h3>
<p>
This web server exists only for <a href="http://onebigsoup.wiki.taoriver.net/moin.cgi/UniversalLineInterface">Universal Line Interface</a> interactions.
</p>

<p>
Please communicate with the wiki by HTTP-POST-ULI.
</p>
</body></html>
"""

THERE_IS_NO_ULI = "%(name)s\nThis server, sadly, does not support ULI interactions.\n"

DEFAULT_NAME = "Default Python HTTP/GET/POST-ULI/redirection Server by http_server.py"

FRAME_TYPE_STRING = "OneBigSoup HTTP Server 1.0"

class UliHttpHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def path_as_list(s):
        not_blank = lambda x:x!=""
        path = filter( not_blank, s.path.split("/") )
        return path

    def basic_response_to( s, line ):
        if line == "ping":
            return "pong"
        elif line == "whoareyou":
            return s.server.name
        elif line == "frametype":
            return FRAME_TYPE_STRING
        elif line == "whoareyou-data":
            return "nLSD description retrival not supported yet."
        else:
            return None

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
            msg = THIS_IS_JUST_ULI % s.server.display_data

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
        
        msg = None

        # this logic can be made nicer.
        # exercise for the reader.
        
        if s.server.basic_responses == True:
            msg = s.basic_response_to( uli_string )
        if (msg==None) and (s.server.uli_func!=None):
            msg = s.server.uli_func( uli_string )
        elif msg==None:
            # assert:
            #   there are no server functions,
            #   the basic response didn't kick in
            msg = THERE_IS_NO_ULI % s.server.display_data

        s.wfile.write( msg )

class UliHttpServer( BaseHTTPServer.HTTPServer ):
    def __init__( s, server_addr,
                  redirect_func=None, get_func=None, uli_func=None,
                  basic_responses=True, nlsd=None,
                  name=DEFAULT_NAME ):
        """
        server_addr: tuple, of the form (HOST_NAME, PORT_NUMBER)
          ex: ("services.taoriver.net",9300)
        
        uli_func( line )   --> returns ULI response line
        get_func( path )   --> returns web page text
        redirect_func( path ) --> returns target URL or None
          (None if there is no redirection to perform.)

        basic_responses: True or False
          True:
             "basic responses" is basic ULI responses, such as
             "ping", (returns "pong",)
             "whoareyou", (returning the name,)
             "frametype", (returning "OneBigSoup HTTP Server 1.0"),
         and "whoareyou-data", (returning an nLSD description of the server)

        nlsd: None - don't worry about yet-
               When nlsd stuff is active and understood,
               this will be data to make available to the nLSD
               world, by basic_responses True "whoareyou-data".
        ---
         
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
        s.basic_responses = basic_responses
        s.nlsd = nlsd
        s.name = name
        
        s.display_data = {"name":s.name}


def run( name, host_name, port_number,
         redirect_func=None, get_func=None, uli_func=None,
         basic_responses=True, nlsd=None):
    """
    name:  friendly name of the server:
           "LocalNames ULI Server" or something like that
    
    host_name:    something like "services.taoriver.net"
    port_number:  something like 80 or 9030 -  whatever you like
    
    redirect_func:
    get_func:       As described in UliHttpServer.__init__.__doc__
    uli_func:
    basic_responses:
    nlsd:
    """
    import http_server
    import time
    httpd = UliHttpServer( (host_name,port_number),
                           redirect_func, get_func, uli_func,
                           basic_responses, nlsd, name )
    print name
    print time.asctime(), "Server Starts - %s:%s" % (host_name, port_number)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.close()
    print name
    print time.asctime(), "Server Stops - %s:%s" % (host_name, port_number)


if __name__ == '__main__':
    run( "testing http_server.py",
         "services.taoriver.net",
         9301 )


