#!/usr/bin/env python

import time
import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer


hostname = "plog.taoriver.net"
port_number = 8000


# Functions you can call:
#
# all_users                             - returns ["user1","user2",...]
# store( username, title, data )        - store data under title
# retrieve( username, title )           - retrieve data under title
# log( username, logtype, logdata )     - record a log entry
# get_logs( username, logtype, maxnum ) - retrieve logs of a given type


# The Personal Log Server stores personal data for "users."
#
# Each server has their own two pieces of data:
#
#  * logs       - Stored in a list, time-stamped.
#                 Each entry is a dictionary.
#                 Mandatory keys:
#                   * "time" - Time the log entry was comitted. (seconds from epic, UTC.)
#                   * "type" - Type identifier. (string, standard. ex: "WikiPost")
#
#  * permanent  - dictionary.

class UserData:
    def __init__( s, name ):
        s.name = name
        s.logs = []
        s.perm = {}

def new_logdata( logtype, logdata ):
    d = { "type": logtype,
          "time": int(time.time()) }
    d.update( logdata )
    return d

class Server:
    def __init__( s ):
        s.userdata = {}

    def run( s, port_num ):
        server = SimpleXMLRPCServer((hostname, port_num), logRequests=0)
        server.register_function( s.all_users )
        server.register_function( s.store )
        server.register_function( s.retrieve )
        server.register_function( s.log )
        server.register_function( s.get_logs )
        print time.asctime(), "Personal Log Server Starts - %s:%s" % (hostname,
                                                                      port_number)
        server.serve_forever()
        print time.asctime(), "Personal Log Server Stops - %s:%s" % (hostname,
                                                                     port_number)
    
    def get_userdata( s, name ):
        """Retrieve UserData object for a particular user."""
        if not s.userdata.has_key( name ):
            s.userdata[ name ] = UserData( name )
        return s.userdata[ name ]

    def all_users( s ):
        """XML-RPC PUBLIC"""
        return s.userdata.keys()
    
    def store( s, username,
               title, data ):
        """XML-RPC PUBLIC"""
        udata = s.get_userdata( username )
        udata.perm[ title ] = data
        return 1
    
    def retrieve( s, username,
                  title ):
        """XML-RPC PUBLIC"""
        udata = s.get_userdata( username )
        return udata.perm.get( title, 0 )
    
    
    def log( s, username, logtype,
             logdata ):
        """XML-RPC PUBLIC"""
        udata = s.get_userdata( username )
        udata.logs.append( new_logdata( logtype,
                                        logdata ) )
        return 1

    def get_logs( s, username, logtype,
                  maxnum, maxage ):
        """
        XML-RPC PUBLIC
        maxnum: Maximum number of entries to return.
        maxage: Maximum age of log entry, in seconds.
        """
        now = int( time.time() )
        current = now - maxage
        
        udata = s.get_userdata( username )
        return filter( lambda x: x["type"]==logtype and x["time"]>current,
                       udata.logs )[-maxnum:]

if __name__ == "__main__":
    server = Server()
    server.run( port_number )


