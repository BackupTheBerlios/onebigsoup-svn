"""
LiveEdit XML-RPC Event Server

Server for hosting collaborative live edits.

"""

import time
import urllib
from SimpleXMLRPCServer import SimpleXMLRPCServer



HOST_NAME    = "services.taoriver.net"
PORT_NUMBER = 9021



class Server:
    """
    Functions you can call:

    * get_update()
    * post_update( text )
    * load_page( name )
    * save_page()

    """
    def __init__( s, host_name, port_number ):
        s.host_name = host_name
        s.port_number = port_number

        s.page_name = ""
        s.page_text = ""

    def get_update(s):
        """
        Get the current info about the page we're working on.
        """
        print "Update returned."
        return { "page_name": s.page_name,
                 "page_text": s.page_text }

    def post_update(s, text ):
        """
        Overwrite the page with the immediate text.
        """
        print "post_update:"
        print text
        s.page_text = text
        return s.get_update()

    def load_page(s, name ):
        """
        Load a MoinMoin wiki page, based on the given URL.

        Later, we can hook this into the LocalNameServer.
        That's why the argument is "name," rather than "URL."

        Later, we can hook this into the EventServer,
        and broadcast that the group is looking at the
        particular page.
        """
        print "load_page:", name
        s.page_name = name
        s.page_text = urllib.urlopen(name+"?action=raw").read()
        return s.get_update()

    def save_page(s, page_text):
        """
        Not only updates page contents,
        but also simultaneously performs a MoinMoin commit.
        """
        s.post_update( page_text )
        params = urllib.urlencode( { 'action' : 'savepage', 'savetext' :
                s.page_text, 'button_save' : 'Save Changes', 'datestamp' : '0',
                'comment' : '', 'notify' : '0', 'rstrip'
                : '1' } )
        urllib.urlopen(s.page_name, params)
        return s.get_update()

    def run( s ):
        server = SimpleXMLRPCServer( (s.host_name, s.port_number),
                                     logRequests=0 )
        server.register_function( s.get_update )
        server.register_function( s.post_update )
        server.register_function( s.load_page )
        server.register_function( s.save_page )
        print time.asctime(), "LiveEdit Server Starts - %s:%s" % (s.host_name,
                                                                  s.port_number)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        print time.asctime(), "LiveEdit Server Stops - %s:%s" % (s.host_name,
                                                                 s.port_number)

if __name__ == "__main__":
    server = Server( HOST_NAME, PORT_NUMBER )
    server.run()
