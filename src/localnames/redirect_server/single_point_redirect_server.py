import time
import BaseHTTPServer
import xmlrpclib
import sys


HOST_NAME = 'services.taoriver.net' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 9091 # Maybe set this to 80
LOCALNAMES_SERVER = "http://services.taoriver.net:9090/"
STARTING_NAMESPACE = "http://onebigsoup.wiki.taoriver.net/moin.cgi/ChannelBotLocalNamesDescription?action=raw"


class MyHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def do_HEAD(s):
        not_blank = lambda x:x!=""
        lookup_list = filter( not_blank, s.path.split("/") )

        try:
            server = xmlrpclib.ServerProxy( LOCALNAMES_SERVER )
            result = server.lookup( STARTING_NAMESPACE,
                                    lookup_list,
                                    1 )
            s.send_response(301)
            s.send_header("Location", result )
            s.end_headers()
        except:
            e = sys.exc_info()[1]
            print "ERROR WHILE PROCESSING PATH:", s.path
            print e
            s.send_response(404)
            s.end_headers()
    def do_GET(s):
        s.do_HEAD()

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
