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

import localnames,time,socket



HOST_NAME    = "services.taoriver.net"
PORT_NUMBER = 9090

PASSWORD    = "password" # client password for receiving ding-ding events

CACHE_TTL_IN_SECONDS = 7*24*60*60 # one week!

ULI_ALLOW_DUMP = True # allow people to dump cache by ULI? (EASILY ATTACKED)



class Server:
    def __init__( s, host_name, port_number, password ):
        s.host_name = host_name
        s.port_number = port_number
        s.password = password

        s.store = localnames.NameSpaceStore( CACHE_TTL_IN_SECONDS )

        s.uli_ns = ""

    def uli(s, message ):
        """
        ULI port:
        * commands are case insensitive
        * one session for all users- hopefully not a big problem..!

        HELP

          Tell how to use the system
        """
        if type(message) != type("string"):
            return "ULI requires string arguments."

        while message[-1] in ["\r","\n"]:
            message = message[:-1]

        message = message.split()
        if len(message)>0:
            cmd = message[0].upper()
            rest = message[1:]
        else:
            cmd = None

        if cmd == "HELP":
            return "\n".join( ["Valid commands are:",
                               "* HELP",
                               "* SET-NAMESPACE (url)",
                               "* LOOKUP (space) (space) ... (name)  --abbreviation: just 'L'",
                               "* DUMP-CACHE (url)",
                               "* LIST-CACHE",
                               "* LIST-NAMES",
                               "* LIST-SPACES",
                               "* LIST-DEFAULTS",
                               "",
                               "Presently set to namespace:",
                               s.uli_ns] )

        if cmd == "SET-NAMESPACE":
            s.uli_ns = rest[0]
            return "Set namespace to: %s\n" % s.uli_ns

        if cmd in ["L","LOOKUP"]:
            return s.lookup( s.uli_ns, rest, 1 ) + "\n"

        if cmd == "DUMP-CACHE":
            url = rest[0]
            if not ULI_ALLOW_DUMP:
                return "Dumping cache by ULI has been turned off."
            if not s.store.namespaces.has_key( url ):
                return "%s wasn't cached." % url
            del s.store.namespaces[ url ]
            return "Cache dumped for namespace by URL %s" % url

        if cmd == "LIST-CACHE":
            return " ".join( s.store.namespaces.keys() ) + "\n"

        if cmd == "LIST-NAMES":
            space = s.store.namespaces.get( s.uli_ns )
            if space == None:
                return "Invalid namespace: %s." % s.uli_ns
            return " ".join( space.names.keys() ) + "\n"

        if cmd == "LIST-SPACES":
            space = s.store.namespaces.get( s.uli_ns )
            if space == None:
                return "Invalid namespace: %s." % s.uli_ns
            return " ".join( space.spaces.keys() ) + "\n"

        if cmd == "LIST-DEFAULTS":
            space = s.store.namespaces.get( s.uli_ns )
            if space == None:
                return "Invalid namespace: %s." % s.uli_ns
            return " ".join( space.defaults ) + "\n"

        return "LocalNames XML-RPC server ULI interface does not understand the request.\n Received: %s\n" % message

    def notify( s, load, client_password ):
        """
        Receives XML-RPC notice,
        using the DingDing v4 interface,
        and OneBigSoup EventConventions.

        Uses them to invalidate or extend namespace cache entries,
        in response to events.
        """
        if client_password != s.password:
            return 0
        # get the URL of the page that was edited,
        if load["Action"] not in ["wikipost2","post"]:
            return 0

        page_url = load.get("PageUrl","")
        page_name = load.get("PageName","")

        # check it against metadata sensitivies, if any.
        for (ns_url, ns) in s.store.namespaces.items():
            what_to_do = "nothing"
            if page_url == ns_url: # the namespace description has changed!
                what_to_do = "invalidate"
            elif page_url == ns.key_values.get("INVALIDATE-UPON-CHANGE-TO"): # the ns desc has changed, by another form!
                what_to_do = "invalidate"
            elif ns.key_values.has_key( "ACCEPT-ADDITION-BY-FORM" ):
                match_against = ns.key_values["ACCEPT-ADDITION-BY-FORM"]
                match_against = match_against.replace("$NAME",page_name)
                if page_url == match_against:
                    what_to_do = "add"
            if what_to_do == "invalidate":
                del s.store.namespaces[ns_url]
            if what_to_do == "add":
                s.store.namespaces[ns_url].names[page_name] = page_url
        return 1


    def locate_list( s, namespace_uri, list_of_words, search_depth ):
        """
        namespace_uri:   URL of namespace to start search from
        list_of_words:   [ "word 1", "word 2", "word 3", ... ]
        search_depth:    1 (always, for now)

        returns:  { "word 1":  resolved URL for word 1,
                    "word 2":  resolved URL for word 2,
                    "word 3":  resolved URL for word 3,
                    ... }

        This function call is confined to one NameSpace.
        You can't route through namespaces.

        However, namespace defaulting works, 1 level deep.

        Added at request of MooKitty.
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
    
    def lookup( s, namespace_uri, lookup_list, search_depth ):
        """
        namespace_uri:  URL of namespace to start search from

        lookup_list:    [ "space", "space", ..., "space", "word" ]

        search_depth:   1 (always, for now)

        returns:  URL resulting from resolving the lookup path

        Follow the connection chaing from namespace_uri to
        the final, target namespace.

        Then, resolve the word. (Note that, it could also be
        a phrase. It just can't include a quotation mark
        inside of it.

        If the word's not found, search 1 level deep into
        the target namespace's defaults.

        If it still isn't found, return error.

        Error codes:
          "NAMESPACE-NOT-FOUND" - namespace wasn't found
          "NOT-FOUND" - word not found
        """
        search = localnames.SpaceTraverser( namespace_uri, s.store )
        try:
            return search.simple_find( lookup_list )
        except localnames.NAME_NOT_FOUND:
            return "NOT-FOUND"
        except localnames.NAMESPACE_NOT_FOUND:
            return "NAMESPACE-NOT-FOUND"
        
    def lookup_many( s, namespace_uri, list_of_lookup_lists, search_depth ):
        """
        namespace_uri:   URL of namespace to start search from

        list_of_lookup_lists:
                         [ ["space", "space", ... , "space", "word"],
                           ... ]
                           
        search_depth:    1 (always, for now)

        returns:  [ URL resulting from path #1,
                    URL resulting from path #2,
                    URL resulting from path #3,
                    ... ]
        """
        return [s.lookup( namespace_uri, sub_list, search_depth ) for sub_list in list_of_lookup_lists]
        
    def list_names(s, ns_URL, path_list):
        """
        List all names at a particular namespace.
        
        ns_URL:     URL of namespace to start from
        path_list:  path to target namespace, could be empty

        NOT IMPLEMENTED YET - PLEASE DON'T PROGRAM TO INTERFACE YET
        """
        pass

    def run( s ):
        server = None
        while server == None:
            try:
                server = DocXMLRPCServer( (s.host_name, s.port_number),
                                      logRequests=0 )
            except socket.error, (code,name):
                server = None
                if code != 98 and name != "Address already in use":
                    raise socket.error(code,name)
                print "couldn't get socket, retrying in 15 seconds..."
                print "   %s %s" % (code,name)
                time.sleep(15)

        server.register_function( s.lookup )
        server.register_function( s.lookup_many )
        server.register_function( s.locate_list )
        server.register_function( s.list_names )
        server.register_function( s.notify )
        server.register_function( s.uli )

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
