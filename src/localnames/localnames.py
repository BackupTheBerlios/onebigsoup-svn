
import marshal


class NameSpaceStore:
    def __init__( s, time_before_reload ):
        s.time_before_reload = time_before_reload
        s.namespaces = {}
    def get( s, ns_url ):
        try: return s.namespaces[ ns_url ]
        except KeyError:
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
        s.ns_url = ns_url
        s.names = {}
        s.gateways = {}
        s.defaults = []
        s.pattern = None
        s._parse_from_url()
        
    def lookup(s, name):
        return s.names.get( name )
    def lookup_gateway(s, name):
        return s.gateways.get( name )
    def list_defaults(s):
        return s.defaults
    def default_for_name(s, name):
        if s.pattern == None:
            return None
        return s.pattern.replace( "$PAGE", name )

    def _parse_from_url(s):
        pass
