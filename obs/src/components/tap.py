#!/usr/bin/env python

import time
import socket
import pprint
from SimpleXMLRPCServer import SimpleXMLRPCServer


HOST_NAME = "services.taoriver.net"
PORT_NUMBER = 9023


# Functions you can call:
#
# notify(source, channel)		- receives notify from event server


class Server:
    def __init__( s, host_name, port_number ):
        s.host_name = host_name
        s.port_number = port_number
    
    def notify(s, load, pw ):
        print "Received:", time.asctime()
        print "Password Given:", pw
        print pprint.pprint( load )
        print "------------------------------------------"
        return 1

    def run( s ):
        server = SimpleXMLRPCServer( (s.host_name, s.port_number),
                                     logRequests=0 )
        server.register_function( s.notify )
        print time.asctime(), "Test Server Starts - %s:%s" % (s.host_name,
                                                              s.port_number)
        server.serve_forever()
        print time.asctime(), "Test Server Stops - %s:%s" % (s.host_name,
                                                             s.port_number)


if __name__ == "__main__":
    server = Server( HOST_NAME, PORT_NUMBER )
    server.run()
