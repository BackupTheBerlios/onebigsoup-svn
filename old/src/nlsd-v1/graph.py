
import urllib
import xmlrpclib


# (  ) FUNCTION
# (  ) FUNCTION-CALL
# (  ) nuke - ability to destroy a subgraph, and perhaps even turn all references to it back into REFs..!
# (  ) Node -1 : None

class Ref:
    """
    Reference to an element in another graph.
    """
    def __init__( s, url, start_pt=None, path=None, store=None ):
        s.url = url
        s.start_pt = start_pt # may be None, indicating "START"
        s.path = path         # may be None, or [], indicating "no path" - generally, a list of indexes to follow
        
        s.store = store       # may be None
        s.pointing_at = None  # may be None
    def __repr__( s ):
        return "<reference into %s>" % ( s.url )
    def surgery( s, src ):
        """
        Change src Python object to point at s.pointing_at,
        rather than me- the Ref.

        Currenlty only works on LISTs and DICT-value references.
        """
        if s.pointing_at == None:
            raise "Wait! Attempted to perform surgery to None. That means I'm not pointing at valid data, by the present None-less model. Are you sure you should be trying to perform this surgery?"
        if sortof_type_str_of(src) == "LIST":
            while s in src:
                where_i_was = src.index(s)
                src[where_i_was] = s.pointing_at
        elif sortof_type_str_of(src) == "DICT":
            for (k,v) in src.items():
                if v == s:
                    src[k] = s.pointing_at
        else:
            raise "Wait! I don't know how to perform surgery on a %s!" % sortof_type_str_of(src)
    def try_to_point(s):
        """
        Try to perform a lookup, IN THE PRESENT STORE.
        If it works, bind s.pointing_at, and return True
        If it fails, bind s.pointing_at to None, and return False
        """
        target_graph = s.store.get_if_already_have( s.url )
        if target_graph==None:
            s.pointing_at = None
            return False
        start_pt = s.start_pt or "START"
        if sortof_type_str_of(start_pt) == "STR":
            reach = target_graph.flags[ start_pt ]
        elif sortof_type_str_of(start_pt) == "INT":
            reach = target_graph.nodes[start_pt]
        else:
            raise "I can't figure out what s.start_pt is: %s" % str(start_pt)
        if s.path == None or s.path == []:
            s.pointing_at = reach
            return True

        # for now, we'll just not worry about indexing beyond reference nodes.
        # this'll work just fine,
        # if you're only indexing within the graph
        for index in s.path:
            try:
                reach = reach[index]
            except TypeError:
                s.pointing_at = None
                return False
        s.pointing_at = reach
        return True
    def resolve(s):
        """
        If the target graph is not present, THIS FUNCTION WILL TRY TO LOAD IT!
        """
        # if the target graph isn't immediately available, we want to load it.
        if not s.try_to_point():
            g = s.store.graph_from_url( s.url )
        s.store.resolve_single_ref(s)
    def resolve_deep(s):
        raise "not implemented yet"

class NotUnderstoodNode:
    """
    A node that we have no idea what it is.
    """
    def __init__( s, node_num, node_type, node_data ):
        s.node_num = node_num
        s.node_type = node_type
        s.node_data = node_data
    def __repr__( s ):
        return "<NotUnderstoodNode: %s %s %s>" % (s.node_num,s.node_type,s.node_data)


def sortof_type_str_of(x):
    """
    Determines if something is *more like* a STR, INT, FLOAT, LIST, DICT, or REF.
    (or XML-RPC)

    This is for the sake of what David Mertz called "pervasive polymorphism."

    (May we never have to process raw text, ever again.)

    This isn't very scientific. If you know a better way, let us know.
    """
    if hasattr(x,"_ServerProxy__host"):
        return "XML-RPC"
    if hasattr(x,"__setitem__"):
        if hasattr(x,"keys"):
            return "DICT"
        if hasattr(x,"append"):
            return "LIST"
    if hasattr(x,"join" ):
        return "STR"
    if hasattr(x,"__add__") and hasattr(x,"__sub__"):
        if hasattr(x,"__and__"):
            return "INT"
        else:
            return "FLOAT"
    if hasattr(x,"url") and hasattr(x,"start_pt"):
        return "REF"
    
def type_str_of(x):
    """
    If you want to be strict to native built-in normal Python types,
    use this function instead, to identify types.
    """
    try:
        # what other way? this is only way I know of, to detect XML-RPC server.
        if x.hasattr(x,"_ServerProxy__host"):
            return "XML-RPC"
        
        return { type("string"): "STR",
                 type(42): "INT",
                 type(42.0): "FLOAT",
                 type([]): "LIST",
                 type({}): "DICT",
                 type(Ref("")): "REF",
                 }[ type(x) ]
    except:
        return "Not a string, int, float, list, or dict."

def escaped(s):
    """
    In future, we'll change:
      slash   -> \\
      newline -> \n
    """
    return s
def unescaped(s):
    return s


class GraphStore:
    """
    Loads graphs, caches them, invokes grand REF resolving.

    1. Load a graph.
    2. Tell every graph: "Nows the time to resolve REFs."

    Also: produces Refs, because they need a link
          back to the GraphStore.
          (This is so you can tell a Ref to automatically
           resolve itself, and everything "just works.")

    Graphs are id'ed by URLs generally, but they don't have to be-
    you could also just give a name of local value, such as: "foo."
    """
    def __init__( s ):
        s.graphs = {} # url --> Graph

    def resolve_references_as_possible(s):
        """
        This function is called after a graph is created or loaded.

        It goes into every graph, checks for REF's in the graph,
        and checks to see if they can link up now.

        If it finds that a REF can now link up, it searches
        for everything that made use of that REF.

        It then surgically replaces the link to the REF
        with the link to the thing that the REF was pointing at.
        """
        refs = []
        resolved = []

        # ask all graphs for REFs
        for graph in s.graphs.values():
            refs.extend( graph.list_of_all_unpointed_refs() )

        # try to resolve all REFs
        for ref in refs:
            if ref.try_to_point():
                resolved.append(ref)

        # for REFs that link up,
        for ref in resolved:
            s.resolve_single_ref( ref )
    def resolve_single_ref( s, ref ):
        # find what points to it
        pointing_to_ref = []
        for graph in s.graphs.values():
            pointing_to_ref.extend( graph.list_of_all_nodes_pointing_to_ref(ref) )

        # surgicly replace links to the REF
        for src in pointing_to_ref:
            ref.surgery(src)

    def resolve_all_refs(s):
        """
        If the target graphs are not loaded, THIS FUNCTION WILL TRY TO LOAD THEM!
        It performs only *ONE PASS*.

        For a deep resolution, see: resolve_all_refs_recursively()
        (Be careful!!! That could be HUGE!)

        Returns: # of references resolved.
        """
        refs = []
        # ask all graphs for REFs
        for graph in s.graphs.values():
            refs.extend( graph.list_of_all_unpointed_refs() )

        # resolve collected refs
        for ref in refs:
            ref.resolve()

        return len( refs )

    def resolve_all_refs_recursively(s):
        """
        BE CAREFUL! DO NOT INDEX THE INTERNET!

        Returns # of passes required to resolve everything.
        """
        passes=0
        while s.resolve_all_refs()>0:
            passes=passes+1
        return passes
    def create_graph_by_string( s, name, nodes_list_string_representation ):
        if s.graphs.has_key( name ):
            raise "There's already a graph by that name!"
        s.graphs[ name ] = Graph( s, data=nodes_list_string_representation )
        s.resolve_references_as_possible()
        return s.graphs[ name ]
    def new_graph( s, name ):
        if s.graphs.has_key( name ):
            raise "There's already a graph by that name!"
        s.graphs[ name ] = Graph( s )
        s.resolve_references_as_possible()
        return s.graphs[ name ]
    def graph_from_url( s, url ):
        try:
            return s.graphs[ url ]
        except KeyError:
            pass
        s.graphs[ url ] = Graph( s, data=urllib.urlopen(url).read() )
        s.resolve_references_as_possible()
        return s.graphs[ url ]
    def get_if_already_have( s, url ):
        return s.graphs.get( url )
    def new_ref(s, url, start_pt=None, path=None ):
        """
        Return a new Ref object, centered on this store.

        Just a convenient notation- not a really necessary function.

        (But maybe in the future, we may track Ref's by way of the store,
         and so we may actually require this function be called.
         If in doubt, when possible, create Refs by this function.)
        """
        return Ref( url, start_pt, path, store=s )

class Graph:
    def __init__( s, store, url=None, ref=None, data=None ):
        """
        required parameters:

        store: the Store that the Graph appears in
          - we may make this None-able in the future
        
        optional parameters:

        url: URL of a graph to read
        ref: Ref object, pointing to graph to read
        data: Raw string data to process
        """
        s.store = store
        
        s.nodes = {} # node#-->Python data item
        s.next_number=0 # assert: ALWAYS valid - see "ensure_next_number_valid"
        
        s.flags = {} # flag name-->Python data item - access by yourself, set with set_flag
        
        s.first_accepted = None # first obj "accepted" (w/ accept func) is first_accepted
        # this is a convenience thing- the very first object accepted
        # is tagged with the default "START" flag, if no other START flag is defined.
        
        if data != None:
            s.read_from_string(data)
        if ref != None:
            s.read_from_reference(data)
        if url != None:
            s.read_from_url(data)

    def resolve_all_refs(s):
        """
        If the target graphs are not loaded, THIS FUNCTION WILL TRY TO LOAD THEM!
        """
        for ref in list_of_all_unpointed_refs():
            ref.resolve()
    def list_of_all_unpointed_refs(s):
        return [node for node in s.nodes.values() if (sortof_type_str_of(node)=="REF" and node.pointing_at==None)]
    def list_of_all_refs(s):
        return [node for node in s.nodes.values() if sortof_type_str_of(node)=="REF"]
    def list_of_all_nodes_pointing_to_ref( s, ref ):
        """
        Presently, only works for LIST and for DICT-value types
        """
        results = []
        for node in s.nodes.values():
            nodetype = sortof_type_str_of(node) 
            if nodetype == "LIST":
                if ref in node:
                    results.append(node)
            elif nodetype == "DICT":
                if ref in node.values():
                    results.append(node)
        return results
    def start(s):
        return s.flags.get( "START" )
    def set_flag( s, name, obj ):
        if s.flags.has_key( name ):
            raise "CAN'T DEFINE FLAGS TWICE!"
        s.flags[ name ] = obj

    def read_from_string(s,data):
        split_comma = lambda x:x.split(",")
        make_ints = lambda l:[int(y) for y in l]
        split_and_intify = lambda x:make_ints(split_comma(x))
        
        lists_to_hook_up=[] # (list,[n,n,n,...])
        dicts_to_hook_up=[] # (dict,[(k,v),(k,v),...])
        flags_to_hook_up=[] # (flag-name, n)
        data = data.splitlines()
        for line in data:
            if line=="" or line=="\n": continue
            try:
                num,ntype,ndata = line.split(":",2)
            except ValueError:
                print "Bad Line: %s" % line
                continue
            num=int(num)
            if ntype=="STR":
                s.add(ndata, num)
            elif ntype=="INT":
                s.add(int(ndata), num)
            elif ntype=="FLOAT":
                s.add(float(ndata), num)
            elif ntype=="LIST":
                s.add([], num)
                hookup = (s.nodes[num],split_and_intify(ndata),)
                lists_to_hook_up.append( hookup )
            elif ntype=="DICT":
                s.add({}, num)
                l=split_and_intify(ndata)
                keys = [x for (i,x) in enumerate(l) if i%2==0]
                values = [x for (i,x) in enumerate(l) if i%2==1]
                kv_pairs_list = zip( keys, values )
                hookup=(s.nodes[num], kv_pairs_list)
                dicts_to_hook_up.append(hookup)
            elif ntype=="FLAG":
                (name,number) = ndata.split(" ")
                number=int(number)
                if s.flags.has_key( name ):
                    raise "Can't have 2 START nodes in one Graph!"                    
                s.set_flag( name, None )
                flags_to_hook_up.append( (name,number) )
            elif ntype=="REF":
                l=ndata.split(" ")
                target_url = l[0]
                if len(l)>1:
                    start_pt = l[1]
                    if start_pt.isdigit():
                        start_pt = int(start_pt)
                else:
                    start_pt = None
                if len(l)>2:
                    path = l[2:]
                else:
                    path = None
                s.add(s.store.new_ref(target_url, start_pt, path), num)
            elif ntype=="XML-RPC":
                print ndata
                s.add(xmlrpclib.ServerProxy(ndata), num)
            else:
                s.add( NotUnderstoodNode( num,ntype,ndata ) )
        for (x, indexes) in lists_to_hook_up:
            l=[s.nodes[index] for index in indexes]
            x.extend(l)
        for (d, kv_pairs_list ) in dicts_to_hook_up:
            for (k,v) in kv_pairs_list:
                (k,v)=s.nodes[k], s.nodes[v]
                d[k]=v
        for (name, index) in flags_to_hook_up:
            s.flags[ name ] = s.nodes[index]
        return s.start()
    
    def has( s, obj ):
        for x in s.nodes.values():
            if id(x) == id(obj):
                return True
        return False
    def index_of( s, obj ):
        for (i,x) in s.nodes.items():
            if id(x) == id(obj):
                return i
        return None
    def ensure_next_number_valid(s):
        while s.nodes.has_key(s.next_number):
            s.next_number=s.next_number+1
    def add(s, obj, index=None):
        if index==None:
            index=s.next_number
        else:
            if s.nodes.has_key(index):
                raise "Adding a node that is already defined!"
        s.nodes[index]=obj
        s.ensure_next_number_valid()
        return index
    def accept( s, obj ):
        """
        TO-DO: make this not based on TYPE,
               but rather, based on CAPABILITIES.
        """
        # we keep track of first thing accepted for API reasons-
        # it makes it easy to choose a START tag, if none was specified
        if s.first_accepted == None:
            s.first_accepted = obj
        # if we already have it, do nothing
        if s.has( obj ): return
        objtype = sortof_type_str_of(obj) # or, could use: type_str_of
        if objtype == "STR":
            return s.add(obj)
        elif objtype == "INT":
            return s.add(obj)
        elif objtype == "FLOAT":
            return s.add(obj)
        elif objtype == "LIST":
            index=s.add(obj)
            for subobj in obj:
                s.accept(subobj)
            return index
        elif objtype == "DICT":
            index=s.add(obj)
            for (key,val) in obj.items():
                s.accept(key)
                s.accept(val)
            return index
        elif objtype == "REF":
            # should I make the ref part of the store?
            obj.store = s.store # I'm gonna say: "yes"
            return s.add(obj)
        elif objtype == "XML-RPC":
            return s.add(obj)
        else:
            raise "Don't understand type of %s" % obj
    def serialize(s):
        if not s.flags.has_key( "START" ) and s.first_accepted != None:
            s.set_flag( "START", s.first_accepted )
        result = []
        for (i,x) in s.nodes.items():
           result.append( "%d:%s:%s" % (i,sortof_type_str_of(x),s.item_text(x)) )
        for name in s.flags:
            result.append( "-1:FLAG:%s %d" % (name,s.index_of(s.flags[name])) )
        return ("\n".join(result))+"\n"
    def list_text( s, l ):
        return ",".join( [str(s.index_of(x)) for x in l] )
    def dict_text( s, d ):
        result = []
        for (k,v) in d.items():
            result.append( str(s.index_of(k)) )
            result.append( str(s.index_of(v)) )
        return ",".join( result )
    def ref_text( s, ref ):
        result = ref.url
        if ref.start_pt != None:
            result = "%s %s" % (result,ref.start_pt)
        if ref.path != None:
            result = "%s %s" % (result," ".join(ref.path))
        return result
    def xmlrpc_text( s, obj ):
        return "http://" + obj._ServerProxy__host
    def item_text( s, obj ):
        "returns one line, no newline at end, no internal newlines"
        objtype = sortof_type_str_of(obj)
        if objtype=="STR":
            return escaped(obj)
        elif objtype=="INT":
            return str(obj)
        elif objtype=="FLOAT":
            return str(obj)
        elif objtype=="LIST":
            return s.list_text( obj )
        elif objtype=="DICT":
            return s.dict_text( obj )
        elif objtype=="REF":
            return s.ref_text( obj )
        elif objtype=="XML-RPC":
            return s.xmlrpc_text( obj )
        else:
            raise "Don't understand type of %s" % obj


