
import marshal
import time


class NameSpaceStore:
    """
    Stores a cache of NameSpace objects, keyed by URL.
    Cache entries expire after a period of time.
    """
    def __init__( s, time_before_reload ):
        """
        time_before_reloaded:
           number of seconds after which cache entries expire
        """
        s.time_before_reload = time_before_reload
        s.namespaces = {}
    def get( s, ns_url ):
        """
        returns NameSpace object
        
        ns_url:
           URL of NameSpace to retrieve
        """
        
        try:
            ns = s.namespace[ ns_url ]
            now = time.time()
            if now < ns.loaded_time + s.time_before_reload:
                return ns
        except KeyError:
            pass
        new_ns = NameSpace( ns_url )
        s.namespaces[ ns_url ] = new_ns
        return new_ns
    def get_if_already_have( s, ns_url ):
        return s.namespaces.get( s, ns_url )
    def save( s, marshal_filename ):
        marshal.dump( s.namespaces, open( marshal_filename, "wb" ) )
    def load( s, marshal_filename ):
        s.namespaces = marshal.load( open( marshal_filename, "rb" ) )


class NameSpace:
    def __init__(s, ns_url):
        """
        Loads NameSpace data, automatically.

        ns_url:
           URL of NameSpace data to load in.
        """
        s.ns_url = ns_url
        s.names = {}
        s.connections = {}
        s.defaults = []
        s.pattern = None
        s.loaded_time = None # filled with time.time() after parse
        s._parse_from_url()
        
    def lookup(s, name):
        """
        returns resolved URL
        """
        return s.names.get( name )
    def lookup_connection(s, name):
        """
        returns resolved URL of gateway
        """
        return s.connections.get( name )
    def list_defaults(s):
        """
        returns list of names of default gateways
        """
        return s.defaults
    def default_for_name(s, name):
        """
        returns a name, made to fit the default page pattern
        """
        if s.pattern == None:
            return None
        return s.pattern.replace( "$PAGE", name )

    def _parse_from_url(s):
        # invoke parser here
        s.loaded_time = time.time()
