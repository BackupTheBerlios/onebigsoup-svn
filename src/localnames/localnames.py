
import cPickle


class NameSpaceStore:
    def __init__( s, time_before_reload ):
        s.time_before_reload = time_before_reload
        s.namespaces = {}
    def get( s, ns_url ):
        if s.namespaces.has_key( ns_url )
            return s.namespaces[ ns_url ]
        new_ns = NameSpace( ns_url )
        s.namespaces[ ns_url ] = new_ns
        return new_ns
    def get_if_already_have( s, ns_url ):
        return s.namespaces.get( s, ns_url, None )
    def save( s, pickle_filename ):
        pickle.dump( s.namespaces, open( pickle_filename, "w" ) )
    def load( s, pickle_filename ):
        s.namespaces = pickle.load( open( pickle_filename, "r" ) )


class NameSpace:
    def __init__(s, ns_url):
        s.ns_url = ns_url
        s.names = {}
        s.gateways = {}
        s.defaults = []
        s.pattern = None
        s._parse_from_url()
        
    def lookup(s, name):
        return s.names.get( name, None )
    def lookup_gateway(s, name):
        return s.gateways.get( name, None )
    def list_defaults(s):
        return s.defaults
    def default_for_name(s, name):
        if s.pattern == None:
            return None
        return s.pattern.replace( "$PAGE", name )

    def _parse_from_url(s):
        pass
