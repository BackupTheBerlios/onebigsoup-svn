
import marshal
import time
import urllib

import lnparser # Sean Palmer's Parser

# TODO: FIX NameSpaceStore.save,
#       which doesn't know how to marshal objects, I guess.

NAMESPACE_FILE_DOESNT_LOAD = "NAMESPACE-FILE-DOESNT-LOAD"
NAME_NOT_FOUND = "NAME-NOT-FOUND"
NAMESPACE_NOT_FOUND = "NAMESPACE-NOT-FOUND"

def name_not_found_error():
    raise NAME_NOT_FOUND

class NameSpaceStore:
    """
    Stores a cache of NameSpace objects, keyed by URL.
    Cache entries expire after a period of time.

    time_before_reload: seconds before cache entries expire
                        (default: 1 day)
    """
    def __init__( s, time_before_reload=24*60*60 ):
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


class Link:
    """
    Keeps information about a particular link.

    Remembers the link's URL, the link's canonical name,
    and a list of names that bind to the link.

    The first name listed is the "canonical" name.

    PROMISES:
    Do not manipulate this, except by way of a LinkStore.
    However, feel free to query it.
    """
    def __init__( s, url, names=None ):
        """
        url: string, the URL that the Link describes
        names: a single name (string), or a list of names

        The first name bound is the "canonical" name.
        """
        s.url = url
        s.names = []
        if type(names)==type("string"):
            s.names.append(names)
        elif type(names)==type(["list","of","names"]):
            s.names.extend(names)
        else:
            raise "Type of 'names' must be either string or list of strings."
    def get_url(s):
        """
        Return URL associated with link.
        """
        return s.url
    def remove_name(s,name):
        """
        Remove a name from the Link's list of names,
        if it is present.
        """
        try:
            s.names.remove(name)
        except ValueError, e:
            pass # name already in list
    def add_name(s, name):
        """
        name: another name to call the Link by
        
        Checks to make sure, first, whether it's already there or not.
        """
        if name not in s.names:
            s.names.append( name )
    def get_names(s):
        """
        Returns a tuple of all names binding to the URL.
        """
        return tuple(s.names)
    def get_canonical_name(s):
        """
        Returns the canonical name, if one was assigned,
        or returns the first name in the internal names list.

        Returns None if no names have been assigned.
        """
        if len(s.names)>0:
            return s.names[0]
        else:
            return None


class LinkStore:
    """
    Keeps a collection of named URLs.

    Two indexes are maintained:
    * upper-case name --> Link
    * URL --> Link

    Links have canonical names, so you can
    get the canonical name as well.
    """
    def __init__(s):
        s.names = {}
        s.urls = {}
    def bind(s, name,url):
        """
        INTERNAL METHOD

        Binds names to URLs, maintaining consistency with two indexes:
        * upper case name --> Link object
        * URL --> Link object
        """
        prior_link = s.names.get( name.upper() )
        if prior_link != None:
            prior_link.remove_name( name )
        link = s.urls.get( url )
        if link != None:
            link.add_name( name )
            s.names[ name.upper() ] = link
        else:
            link = Link( url, name )
            s.names[ name.upper() ] = link
            s.urls[ url ] = link
    def lookup(s, name):
        """
        Given a name, look up it's URL.
        Case insensitive.
        """
        link = s.names.get(name.upper())
        if link:
            return link.get_url()
        else:
            return None
    def canonical_names(s):
        results=[]
        for link in s.urls.values():
            results.append(link.get_canonical_name())
        results = [x for x in results if x != None]
        return results
    def canonical_name_for_name(s, name):
        link = s.names[name.upper()]
        return link.get_canonical_name()
    def canonical_name_for_url(s, url):
        link = s.urls[url]
        return link.get_canonical_name()

class NameSpace:
    """
    A NameSpace keeps information about a LocalNames name space.

    This information includes:
     * URL of the name space
     * names table (name-URL bindings)
     * name-Link and URL-Link indexes over the names table
     * neighboring spaces table
     * name-Link and URL-Link indexes over the neighboring spaces table
     * list of neighboring spaces, for defaulting
     * last resort name pattern, for when a name space exhausts
       all other ways of binding names to URLs
     * key-value metadata about the name space
     * record of when the name space was loaded
    """
    def __init__(s, ns_url):
        """
        ns_url: URL of the name space description
        
        Loads NameSpace data, automatically.

        ns_url:
           URL of NameSpace data to load in.
        """
        s.ns_url = ns_url

        s.names = LinkStore() # names table
        s.spaces = LinkStore() # spaces table
        s.defaults = [] # list of names, in any form
        
        s.key_values = {} # metadata about the name space
        
        s.last_resort_name_pattern = None # if name can't be resolved...
        
        s.loaded_time = None # filled with time.time() after parse
        
        s._parse_from_url()
        
    def lookup_name(s, name):
        """
        returns resolved URL
        """
        return s.names.lookup( name )
    def lookup_space(s, name):
        """
        returns resolved URL of name space description
        """
        return s.spaces.lookup( name )
    def default_for_name(s, name):
        """
        returns a name, made to fit the default page pattern
        """
        if s.last_resort_name_pattern == None:
            return None
        return s.last_resort_name_pattern.replace( "$NAME", name )
    def bind_name_to_url(s, name, url):
        """
        Bind a Name to a URL.
        """
        s.names.bind( name, url )
    def bind_namespace_to_url(s, name, url ):
        """
        Same as bind_name_to_url, but for names
        of other name spaces.
        """
        s.spaces.bind( name, url )
    def _parse_from_url(s):
        """
        This internal function parses the page at the URL
        and fills out the NameSpace based on the found page.

        Raises NAMESPACE_FILE_DOESNT_LOAD if URL isn't found.

        After parsing out the description, NameSpace is time stamped.
        """
        parser = lnparser.Parser( LocalNamesSink(s) )
        try:
            parser.feedUrl( s.ns_url )
        except IOError,e:
            raise NAMESPACE_FILE_DOESNT_LOAD
        parser.parse()
        s.loaded_time = time.time()
    def canonical_names(s):
        return s.names.canonical_names()
    def canonical_names_of_spaces(s):
        return s.spaces.canonical_names()

class LocalNamesSink:
    """
    Sinks data from the parser into a NameSpace object.
    """
    def __init__(self, namespace):
        self.namespace = namespace

    def meta(self, key, value):
        self.namespace.key_values[key] = value

    def map(self, name, uri):
        self.namespace.bind_name_to_url( name,uri )

    def otherNameSpace( self, name, uri ):
        self.namespace.bind_namespace_to_url( name, uri )

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

        return s.lookup_name_one_deep( path[-1] ) or s.default_for_name( path[-1] ) or name_not_found_error()

    
class Resolver:
    """
    Facade, simulating being based over a particular namespace url.
    """
    def __init__( s, default_ns_url, store_filename, store=None ):
        """
        default_ns_url: URL of namespace to start from
        store_filename: for save & load functions
        store: (optional) pre-existing store to use
        """
        s.store = store
        s.store_filename = store_filename
        s.default_ns_url = default_ns_url
        
        if s.store == None:
            s.store = NameSpaceStore()
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
