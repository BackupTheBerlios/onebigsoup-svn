
import marshal
import time
import urllib

import lnparser # Sean Palmer's Parser

# TODO: FIX NameSpaceStore.save,
#       which doesn't know how to marshal objects, I guess.

NAME_NOT_FOUND = "NAME-NOT-FOUND"
NAMESPACE_NOT_FOUND = "NAMESPACE-NOT-FOUND"

def name_not_found_error():
    raise NAME_NOT_FOUND

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

        will look it up, if not already cached
        
        ns_url:
           URL of NameSpace to retrieve
        """
        
        try:
            ns = s.namespaces[ ns_url ]
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
        s.spaces = {}
        s.key_values = {}
        s.defaults = []
        s.last_resort_name_pattern = None
        s.loaded_time = None # filled with time.time() after parse
        s._parse_from_url()
        
    def lookup_name(s, name):
        """
        returns resolved URL
        """
        return s.names.get( name )
    def lookup_space(s, name):
        """
        returns resolved URL of gateway
        """
        return s.spaces.get( name )

    def default_for_name(s, name):
        """
        returns a name, made to fit the default page pattern
        """
        if s.last_resort_name_pattern == None:
            return None
        return s.last_resort_name_pattern.replace( "$NAME", name )

    def _parse_from_url(s):
        parser = lnparser.Parser( LocalNamesSink(s) )
        parser.feedString( urllib.urlopen( s.ns_url ).read() )
        parser.parse()
        s.loaded_time = time.time()

class LocalNamesSink:
    """
    Sinks data from the parser into a NameSpace object.
    """
    def __init__(self, namespace):
        self.namespace = namespace

    def meta(self, key, value):
        self.namespace.key_values[key] = value

    def map(self, name, uri):
        self.namespace.names[ name ] = uri

    def otherNameSpace( self, name, uri ):
        self.namespace.spaces[ name ] = uri

    def defaultNameSpaces(self, name):
        self.namespace.defaults.append( name )

    def lastResortNamePattern(self, pattern):
        self.namespace.last_resort_name_pattern = pattern


class SpaceTraverser:
    """
    A namespace traverser that can be guided, step by step.
    
    It can go many different ways-
    You make the major decisions, it carries them out,
    and tells you where it's at.

    It effectively wraps around the namespace it's visiting.
    """
    def __init__( s, start_ns_url, store ):
        s.store = store
        s.ns = s.store.get( start_ns_url )

    def lookup_name( s, name ):
        "Wrapper function around NameSpace visiting"
        return s.ns.lookup_name( name )
    def lookup_space( s, name ):
        "Wrapper function around NameSpace visiting"
        return s.ns.lookup_space( name )
    def default_for_name( s, name ):
        "Warpper function around NameSpace visiting"
        return s.ns.default_for_name( name )

    def enter_space( s, name ):
        "Identify the target namespace, and go there"
        target_space_url = s.ns.lookup_space( name )
        if target_space_url == None:
            raise NAMESPACE_NOT_FOUND
        s.ns = s.store.get( target_space_url )

    def enter_spaces( s, names ):
        # copy the hop_list
        hop_list = list( names )

        # traverse list
        while len(hop_list)>0:
            s.enter_space( hop_list.pop(0) )
        
    def lookup_name_one_deep( s, name ):
        # is it defined here?
        local_lookup = s.lookup_name( name )
        if local_lookup != None:
            return local_lookup

        # is it around us? (in a "subspace?")
        
        # get the name from defaults,
        for subspace_name in s.ns.defaults:
            # turn it into a NS URL,
            subspace_url = s.ns.lookup_space( subspace_name )
            # get the NS,
            subspace_ns = s.store.get( subspace_url )
            # look for the entry,
            subspace_lookup = subspace_ns.lookup_name( name )
            # if it's there,
            if subspace_lookup != None:
                # return it
                return subspace_lookup

        # not found
        return None

    def simple_find( s, path ):
        """
        path: ["space-name","space-name",...,"space-name","entry-name"]

        1. go to target space
             - raise NAMESPACE_NOT_FOUND if path not possible
        2. return name if present
        3. return name if found in defaults
        4. raise NAME_NOT_FOUND if none of the above
        """
        s.enter_spaces( path[:-1] )

        return s.lookup_name_one_deep( path[-1] ) or s.default_for_name( path[-1] ) or name_not_found()

    
class Resolver:
    """
    Facade over the whole system.
    """
    def __init__( s, default_ns_url, store_filename, store=None ):
        s.store = store
        s.store_filename = store_filename
        s.default_ns_url = default_ns_url
        
        if s.store == None:
            s.store = NameSpaceStore(24*60*60) # one full day
            try:
                s.store.load(store_filename)
            except IOError:
                # file not found? it's okay.
                pass
        
    def save(s):
        s.store.save(s.store_filename)

    def simple_find( s, path ):
        """
        Performs a simple_find search
        (see PathTraverser), rooted in the
        resolver's base namespace.
        """
        traverser = SpaceTraverser( s.default_ns_url, s.store )
        return traverser.simple_find( path )



def test_resolver():
    print "READING:"
    print urllib.urlopen("http://lion.taoriver.net/localnames.txt").read()
    print "------"
    resolver = Resolver( "http://lion.taoriver.net/localnames.txt",
                         "localnames_cache" )
    print resolver.simple_find( ["WeirdFile"] )
    print resolver.simple_find( ["MarshallBrain"] )
    print resolver.simple_find( ["/."] )
    print resolver.simple_find( ["OneBigSoup","FrontPage"] )
    print resolver.simple_find( ["OneBigSoup","DingDing"] )
    print resolver.simple_find( ["LocalNames"] )
    print resolver.simple_find( ["FrontPage"] )
    
    
if __name__=="__main__": 
    test_resolver()
