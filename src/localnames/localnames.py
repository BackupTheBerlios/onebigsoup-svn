
import marshal
import time
import urllib

import lnparser # Sean Palmer's Parser

# TODO: FIX NameSpaceStore.save,
#       which doesn't know how to marshal objects, I guess.


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
    def comment(self, s):
        pass

    def meta(self, key, value):
        pass

    def map(self, name, uri):
        self.namespace.names[ name ] = uri

    def connection(self, name, uri):
        self.namespace.connections[ name ] = uri

    def defaultConnection(self, name):
        self.namespace.defaults.append( name )

    def defaultPagePattern(self, pattern):
        self.namespace.pattern = pattern


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

    def lookup_tuple( s, tup ):
        """
        (1) Follows connections chain.

        (2) Looks for name,
            and checks 1 level into defaults, too.

        (3) Returns against last connection's pattern,
            if nothing found.

        Doesn't check defaults on Connections.
        
        returns URL or None
        
        tup:
           tuple where first items are connection names,
           and last item is the name of an item
        """
        space = s.store.get( s.default_ns_url )
        final_name = tup[-1]

        # Go through all the Connections first...
        connection_list = list(tup[:-1])
        connection_list.reverse() # we're going to pop
        while len(connection_list)>0:
            next_space_name = space.lookup_connection( connection_list.pop() )
            if next_space_name == None:
                return None # can't resolve :(
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
        return space.default_for_name( final_name )

def test():
    store = NameSpaceStore(24*60*60) # one day timeout
    space = store.get( "http://taoriver.net/tmp/nstest.txt" )
    print space.lookup( "FirstName" )

def test_resolver():
##     resolver = Resolver( "http://onebigsoup.wiki.taoriver.net/moin.cgi/LocalNamesDescription?action=raw",
##                          "localnames_cache" )
##     print resolver.lookup_tuple( ["FrontPage"] )
##     print resolver.lookup_tuple( ["Robots"] )
##     print resolver.lookup_tuple( ["PublicEmail"] )
##     print resolver.lookup_tuple( ["IntComm", "OneBigSoup"] )
##     print resolver.lookup_tuple( ["IntComm", "CommunityWiki", "OneBigSoup"] )
##     print resolver.lookup_tuple( ["CommunityWiki", "OneBigSoup"] )
##     print resolver.lookup_tuple( ["ThePublicWeb"] )
    resolver = Resolver( "http://lion.taoriver.net/localnames.txt",
                         "localnames_cache" )
    print resolver.lookup_tuple( ["WeirdFile"] )
    print resolver.lookup_tuple( ["Kitty"] )
    print resolver.lookup_tuple( ["MarshallBrain"] )
    print resolver.lookup_tuple( ["/."] )
    print resolver.lookup_tuple( ["OneBigSoup","FrontPage"] )
    print resolver.lookup_tuple( ["OneBigSoup","DingDing"] )
    print resolver.lookup_tuple( ["LocalNames"] )
    
    
if __name__=="__main__": 
    test()
    print "---------"
    test_resolver()
