"""
LocalNames lookup XML-RPC Event Server

  thin wrapper around the resolver in localnames.py



Subscription:

server = xmlrpclib.ServerProxy( "http://services.taoriver.net:9011/" )
server.subscribe( ["VAL","Action","wikipost2"],
                  { "CLIENT-XMLRPC": "http://services.taoriver.net:9090/" }, "password" )
server.subscribe( ["VAL","Action","post"],
                  { "CLIENT-XMLRPC": "http://services.taoriver.net:9090/" }, "password" )

"""

from DocXMLRPCServer import DocXMLRPCServer

import localnames,time



HOST_NAME    = "services.taoriver.net"
PORT_NUMBER = 9090

PASSWORD    = "password" # client password for receiving ding-ding events

CACHE_TTL_IN_SECONDS = 7*24*60*60 # one week!



class Server:
    """
    Functions you can call:

    * resolve( from_namespace, lookup_list, search_depth )

    Presently, max_depth doesn't work.
    It's always just 1 (numeric), and only applies
    to the final name in the lookup_tuple.
    """
    def __init__( s, host_name, port_number, password ):
        s.host_name = host_name
        s.port_number = port_number
        s.password = password

        s.store = localnames.NameSpaceStore( CACHE_TTL_IN_SECONDS )

    def notify( s, load, client_password ):
        if client_password != s.password:
            return 0
        # get the URL of the page that was edited,
        if load["Action"] not in ["wikipost2","post"]:
            return 0

        page_url = load.get("PageUrl","")
        page_name = load.get("PageName","")
        print "RECEIVED:", page_name, page_url
        # check it against metadata sensitivies, if any.
        for (ns_url, ns) in s.store.namespaces.items():
            what_to_do = "nothing"
            if page_url == ns_url: # the namespace description has changed!
                what_to_do = "invalidate"
            elif page_url == ns.meta.get("INVALIDATE-UPON-CHANGE-TO"): # the ns desc has changed, by another form!
                what_to_do = "invalidate"
            elif ns.meta.has_key( "ACCEPT-ADDITION-BY-FORM" ):
                match_against = ns.meta["ACCEPT-ADDITION-BY-FORM"]
                match_against = match_against.replace("$NAME",page_name)
                if page_url == match_against:
                    what_to_do = "add"
            print "CONSIDERING FOR:", ns_url
            print "DECISION:", what_to_do
            if what_to_do == "invalidate":
                del s.store.namespaces[ns_url]
            if what_to_do == "add":
                s.store.namespaces[ns_url].names[page_name] = page_url
        print "-------------\n\n"
        return 1

    def locate_list( s, namespace_uri, list_of_words, search_depth ):
        """
        Added at request of MooKitty.

        Returns a dictionary: word:URL.
        """
        results = {}
        
        for word in list_of_words:
            try:
                result = s.lookup( namespace_uri, [word,], search_depth )
                if result == None:
                    result = "NOT-FOUND"
            except:
                result = "ERROR"
            results[word] = result
            
        return results
    
    def lookup_many( s, from_namespace, list_of_lookup_lists, search_depth ):
        """
        Just call lookup repeatedly.
        
        list_of_lookup_lists is a list of lists.

        returns a list
        """
        results = []
        for sub_list in list_of_lookup_lists:
            try:
                result = s.lookup( from_namespace, sub_list, search_depth )
                if result == None:
                    result = "NOT-FOUND"
            except:
                result = "ERROR"
            results.append( result )
        return results
        
    def lookup( s, from_namespace, lookup_list, search_depth ):
        """
        (1) Follows connections chain.

        (2) Looks for name,
            and checks 1 level into defaults, too.

        (3) Returns against last connection's pattern,
            if nothing found.

        Doesn't check defaults on Connections.
        
        returns URL or None
        
        lookup_list:
           list where first items are connection names,
           and last item is the name of an item

        Examples:

        lookup( "http://lion.taoriver.net/localnames.txt",
                ["SlashDot"],
                1 )

        lookup( "http://lion.taoriver.net/localnames.txt",
                ["CommunityWiki","OneBigSoup"],
                1 )
        """
        space = s.store.get( from_namespace )
        final_name = lookup_list[-1]

        # Go through all the Connections first...
        connection_list = list(lookup_list[:-1])
        connection_list.reverse() # we're going to pop
        while len(connection_list)>0:
            next_space_name = space.lookup_connection( connection_list.pop() )
            if next_space_name == None:
                return "NAMESPACE-NOT-FOUND" # can't resolve :(
            space = s.store.get( next_space_name )

        # okay, we've got the final space
        # now look up the term
        url = space.lookup( final_name )
        if url != None:
            return url

        # okay, wasn't there, so lets check the defaults.
        for subspace in [s.store.get(space.lookup_connection(name)) for name in space.list_defaults()]:
            url=subspace.lookup( final_name )
            if url != None:
                return url

        # didn't find anything. whattawe do?
        # go to our default space, and return our default pattern match
        default = space.default_for_name( final_name )
        if default != None:
            return default
        return "NOT-FOUND"


    def run( s ):
        server = DocXMLRPCServer( (s.host_name, s.port_number),
                                  logRequests=0 )
        server.register_function( s.lookup )
        server.register_function( s.lookup_many )
        server.register_function( s.locate_list )
        server.register_function( s.notify )

        print time.asctime(), "LocalNames Server Starts - %s:%s" % (s.host_name,
                                                                    s.port_number)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        server.close() # might work..?
        print time.asctime(), "LocalNames Server Stops - %s:%s" % (s.host_name,
                                                                   s.port_number)

if __name__ == "__main__":
    server = Server( HOST_NAME, PORT_NUMBER, PASSWORD )
    server.run()
