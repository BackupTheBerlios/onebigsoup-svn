#
# v5 - adding Ref from Graph
#
#    LEO:
#    WORK IN PROGRESS:
#    SEARCH DOCUMENT FOR "LEO" FOR ALL WORK THAT NEEDS
#    TO BE DONE TO COMPLETE REF--GRAPH TIES..!
#
# CONCEPTS TO ADD:
#
# * Ref from Graph, so you can automatically de-reference,
#     just by talking to it.
# * downloading URL
# * downloading on demand
# * uploading to URL (incl save to file:///)
#
# SUPPORTS TO ADD:
#
# * More sophisticated policy controls.
# * index id->zone
# * polish API (lots of renaming...)
#
# DOT I & CROSS T:
#
# * check every type(...) check, and make it generic/polymorphic
# * polish names
# * code at 70 columns
# * lookup Python coding conventions, and apply
#
# BUGS: (fix NOW!)
#
# * numbering: if you name a node by flag assignment,
#              you can't immediately xml it out
# * Zone.xml crashes in rendering list items
# * If you add Ref objects, and then replace them
#   with, say, a number or a string, is the old
#   Ref still in the graph? (Do we "accumulate
#   junk," and do we have a way of cleaning it
#   out, ideally automatically?)
#

import xml.sax.handler
import xml.sax

# policy
STOP_WILD = 1
STOP_OTHER_ZONE = 2
STOP_SAME_ZONE = 4
STOP_AFTER_ONE_DEEP = 8
GO_NOWHERE = 7
GO_EVERYWHERE = 0


class Ref:
    def __init__( s, graph, url, index=0 ):
        """
        You rarely initialize this yourself;
        Rather, get a Graph to make one for you.

	This is the graph that will load the
	target Zone, should that become necessary.
        """
        s.graph = graph
        s.url = url
        s.index = index
    def resolve(s):
        s.graph.replace_ref( s )
    def __repr__( s ):
        return "Ref( %s, %s )" % (repr(s.url), repr(s.index))
    def __eq__( s, other ):
        L=dir(other)
        if "graph" not in L:
            return False
        if "url" not in L:
            return False
        if "index" not in L:
            return False
        return other.graph == s.graph and other.url == s.url and other.index == s.index

class NativeIntegerInfo:
    def __init__( s, node ):
        s.node = node
    def xml_identifier(s):
        return "integer"
    def get_neighbors( s ):
        return []
    def one_per_graph( s ):
        return True
class NativeFloatInfo:
    def __init__( s, node ):
        s.node = node
    def xml_identifier(s):
        return "float"
    def get_neighbors( s ):
        return []
    def one_per_graph( s ):
        return True
class NativeStringInfo:
    def __init__( s, node ):
        s.node = node
    def xml_identifier(s):
        return "string"
    def get_neighbors( s ):
        return []
    def one_per_graph( s ):
        return True
class NativeListInfo:
    def __init__( s, node ):
        s.node = node
    def xml_identifier(s):
        return "list"
    def get_neighbors( s ):
        return s.node
    def one_per_graph( s ):
        return False
    def replace_ref( s, ref_node, real_node ):
        while ref_node in s.node:
            index = s.node.index( ref_node )
            s.node[index]=real_node

    def place_ref( s, graph, neighbor_node ):
        """
        You MUST specify Graph, the graph to look
	up the reference in.
        The NativeListInfo has no concept of what
        Graph you are connected to, and can't look
	up Zone & Zone Index information without it.
        """
	ref=graph.ref_to_node( neighbor_node )
	s.place_known_ref( neighbor_node, ref )
    def place_known_ref( s, neighbor_node, ref ):
        while neighbor_node in s.node:
            index = s.node.index( neighbor_node )
            s.node[index]=ref
class NativeDictionaryInfo:
    def __init__( s, node ):
        s.node = node
    def xml_identifier(s):
        return "dictionary"
    def get_neighbors( s ):
        return s.node.keys() + s.node.values()
    def one_per_graph( s ):
        return False
    def replace_ref( s, ref_node, real_node ):
        for (k,v) in s.node.items():
            if k == ref_node:
                s.node[ real_node ] = v
                del s.node[ k ]
            if v == ref_node:
                s.node[ k ] = real_node
    def place_ref( s, graph, neighbor_node ):
        """
        You MUST specify Graph, the graph to look
	up the reference in.
        The NativeListInfo has no concept of what
        Graph you are connected to, and can't look
	up Zone & Zone Index information without it.
        """
	ref=graph.ref_to_node( neighbor_node )
	s.place_known_ref( neighbor_node, ref )
    def place_known_ref( s, neighbor_node, ref ):
        for (k,v) in s.node.items():
            if k == neighbor_node:
                s.node[ ref ] = ref
                del s.node[ k ]
            if v == neighbor_node:
                s.node[ k ] = ref
class RefInfo:
    def __init__( s, node ):
        s.node = node
    def xml_identifier(s):
        return "reference"
    def get_neighbors( s ):
        return []
    def one_per_graph( s ):
        return True
class DummyInfo:
    def __init__( s, node ):
        s.node = node
        print "Don't know how to handle:", s.node
    def xmlidentifier(s):
        return "dummy" # This is actually an error. Should never appear.
    def get_neighbors( s ):
        return []
    def one_per_graph( s ):
        return True

def type_info( node ):
    if type( node ) == type( 42 ):
        return NativeIntegerInfo( node )
    if type( node ) == type( 42.0 ):
        return NativeFloatInfo( node )
    if type( node ) in [type( "" ),type( u"" )]:
        return NativeStringInfo( node )
    if type( node ) == type( [] ):
        return NativeListInfo( node )
    if type( node ) == type( {} ):
        return NativeDictionaryInfo( node )
    if "url" in dir( node ) and "index" in dir( node ):
        return RefInfo( node )
    return DummyInfo( node )

class Graph:
    def __init__( s ):
        s.zones = []
    def register_zone( s, zone ):
        """called by zone __init__"""
        assert zone not in s.zones, "Double added zone to graph."
        s.zones.append( zone )
    def get_zone_for_node( s, node ):
        """
        Return Zone containing node.
        Return None if the node is wild.

        Also returns None if the node is of the type
        where you have one in each zone.
        That way, strings and integers aren't
        repeated in every graph.
        """
        for zone in s.zones:
            if zone.contains( node ):
                return zone
        return None # "wild"
    def get_zone_with_url( s, url, retrieve_from_url=False ):
        for zone in s.zones:
            if zone.url == url:
                return zone
        if retrieve_from_url==True:
            zone = Zone( url, s )
            zone.read()
            return zone
        return None
    def ref( s, url, index ):
        return Ref( s, url, index )
    def ref_to_node( s, node ):
	zone=s.get_zone_for_node( node )
	url=zone.get_url()
	index=zone.number_node( node )
	return Ref( s, url, index )
    def replace_ref( s, ref ):
	"""
	Make replacements for a *single* Ref.

	Note that: If the Ref hasn't been absorbed yet,
	it won't resolve.

	If you want to make DAMN sure that it's going to
	be replaced, do a "graph.absorb()", call, to
	re-absorb everything, everywhere.

	Assumption: Ref ONLY used in Zone containing it.

	This function has POOR performance.
	"""
	zone=s.get_zone_for_node( ref )
        assert zone != None, "No zone! I can't make replacements for a node that no Zone knows about..!"
	zone.replace_refs( this_ref_only = ref )
	
    def find_ref_target( s, ref, retrieve_from_url=False ):
        """
        Return target if found; Otherwise, return None.
        """
        zone = s.get_zone_with_url( ref.url, retrieve_from_url )
        if not zone:
            return None
        return zone.get( ref.index )
    def replace_refs_for( s, node,
		          retrieve_from_url=False,
		          this_ref_only=None ):
        """
        Replace Ref's if their targets are available.
        If not, leave it as a Ref.

	(Does this function need to be in Graph?
	 It seems that we could take it out, so that
	 you could replace refs for data that is not
	 inside of a graph.)
        """
        for neighbor_node in type_info( node ).get_neighbors():
            if type_info( neighbor_node ).__class__ == RefInfo:
		if this_ref_only and neighbor_node != this_ref_only:
		    continue
                target = s.find_ref_target( neighbor_node, retrieve_from_url )
                if target:
                    ti = type_info( node )
                    ti.replace_ref( neighbor_node, target )
    def place_refs_for( s, node ):
        """
        Place Ref's if the target is in another zone.
        """
        this_zone = s.get_zone_for_node( node )
        ti=type_info( node )
        for neighbor_node in ti.get_neighbors():
            if type_info( neighbor_node ).one_per_graph():
                continue
            target_zone = s.get_zone_for_node( neighbor_node )
            if target_zone != this_zone and target_zone != None:
                target_index = target_zone.number_node( neighbor_node )
		ref=s.ref( target_zone.url, target_index )
		ti.place_known_ref( neighbor_node, ref )
    def replace_refs( s ):
        for zone in s.zones:
            zone.replace_refs()
    def place_refs( s ):
        for zone in s.zones:
            zone.place_refs()
    def visit( s, node, action, policy, context=None ):
        if context==None:
            context={}
        if id(node) in context:
            return
        apply( action, (node,) )
        context[ id(node) ] = node
        this_zone = s.get_zone_for_node( node )
        for neighbor_node in type_info( node ).get_neighbors():
            target_zone = s.get_zone_for_node( neighbor_node )
            if (policy & STOP_WILD) and target_zone == None:
                continue
            if (policy & STOP_OTHER_ZONE) and target_zone != None and target_zone != this_zone and type_info( neighbor_node ).one_per_graph() == False:
                # "STOP_OTHER_ZONE?"
                # "If it's zoned, and it's not in *this* zone, then get out of here,"
                # "Oh yeah, if it's one-per-graph, that's OKAY, we'll pick it up,
                #  but otherwise: outta here! It belongs in just one Zone"
                continue
            if (policy & STOP_SAME_ZONE) and target_zone != None and target_zone == this_zone:
                continue
            
            if ( policy & STOP_AFTER_ONE_DEEP ):
                s.visit( neighbor_node, action, GO_NOWHERE, context )
            else:
                s.visit( neighbor_node, action, policy, context )
        return

class Zone:
    def __init__( s, url, graph=None ):
        s.url = url

        if graph:
            s.graph = graph
        else:
            s.graph = Graph()

        s.graph.register_zone( s )

        s.id_to_object = {} # ID# to ACTUAL OBJECT
        
        s.index_to_object = {} # NUMERICAL and STRING ("flag") indexes
        s.id_to_index = {} # should ONLY point to NUMERICAL indexes

    def _include_object( s, obj ):
        """
        All writes to id_to_object MUST go by this function.
        """
        s.id_to_object[ id(obj) ] = obj
    def _bind_index_to_node( s, index, obj ):
        """
        All writes to id_to_index or index_to_object MUST
        go by this function.
        """
        if type( index ) == type( "string" ):
            s.index_to_object[ index ] = obj
        elif type( index ) == type( 42 ):
            s.index_to_object[ index ] = obj
            s.id_to_index[ id(obj) ] = index
    
    def stat(s):
        """
        STAT!
        Use while debugging.
        """
        import pprint
        print "url: %s" % s.url
        print "id->object:"
        pprint.pprint( s.id_to_object )
        print "index->object:"
        pprint.pprint( s.index_to_object )
        print "id->index:"
        pprint.pprint( s.id_to_index )
    def get_graph( s ):
        return s.graph
    def get_url( s ):
        return s.url

    def contains( s, node ):
        if id(node) in s.id_to_object:
            return True
        return False

    def absorb( s, node=None ):
        """
        Absorb node, and all attached nodes.
        Note that we do NOT absorb nodes that are already in other Zones.

        If you do not specify a node, then it does a "re-absorb."
        That is, it goes to each node, and performs an absorb from it.
        The net result is that everything that the Zone can see-
        it belongs either to this Zone (old or newly absorbed,)
        or it belongs to another Zone (old).
        """
        if node:
            s.graph.visit( node, s.absorb_one, STOP_OTHER_ZONE )
        else:
            for node in s.id_to_object.values():
                s.graph.visit( node, s.absorb_one, STOP_OTHER_ZONE )
    def absorb_one( s, node ):
        s._include_object( node )

    def replace_refs( s, retrieve_from_url=False, this_ref_only=None ):
        for node in s.id_to_object.values():
            s.graph.replace_refs_for( node, retrieve_from_url, this_ref_only )
    def place_refs( s ):
        for node in s.id_to_object.values():
            s.graph.place_refs_for( node )
            # pick up the new references
            s.graph.visit( node, s.absorb_one, STOP_OTHER_ZONE | STOP_AFTER_ONE_DEEP )
    
    def number( s, number_from = 0 ):
        for node in s.id_to_object.values():
            number_from = s.number_node( node, number_from )+1

    def number_node( s, node, number_node = 0 ):
        """
        Return a node's number.
        If it doesn't have one, assign one, and return it.
        """
        # don't renumber,
        index = s.id_to_index.get( id(node) )
        if index != None:
            return index
        # don't use a number twice,
        while number_node in s.index_to_object.keys():
            number_node=number_node+1
        # link both ways
        s._bind_index_to_node( number_node, node )
        return number_node

    def __getitem__( s, index ):
        return s.index_to_object[ index ]
    def __setitem__( s, key, value ):
        s.absorb( value )
        s._bind_index_to_node( key, value )
        
    def __len__( s ):
        return len( s.id_to_object )
    def __contains__( s, node ):
        return s.contains( node )
    def get( s, index, last_resort=None ):
        return s.index_to_object.get( index, last_resort )

    def xml( s ):
        # make sure nothing is left in the wild
        s.absorb()
        # make sure that we only hold References to outside objects.
        s.place_refs()
        # make sure every node is numbered
        s.number()

        # place_refs MUST be called before number.
        # (That way, new Ref's are numbered.)

        output = []

        output.append( u'''<?xml version="1.0" standalone="yes"?>''' )
        output.append( u'''''' )
        output.append( u'''<zone>''' )
        L=s.index_to_object.items()
        L.sort()
        for (index,obj) in L:
            ti=type_info( obj )
            if type(index)==type("string"):
                int_index=s.id_to_index[ id(obj) ]
                output.append( u'''  <flag at="%d" name=%s"/>''' % (int_index,index) )
            elif ti.xml_identifier() == "integer":
                output.append( u'''  <integer id="%d">%d</integer>''' % (index,obj) )
            elif ti.xml_identifier() == "float":
                output.append( u'''  <float id="%d">%f</integer>''' % (index,obj) )
            elif ti.xml_identifier() == "list":
                output.append( u'''  <list id="%d">''' % index )
                for neighbor_node in obj:
                    if type_info( neighbor_node ).one_per_graph()==False:
                        assert s.graph.get_zone_for_node( neighbor_node ) == s, "somehow, the neighboring node is in another graph?! Node: %s" % repr( neighbor_node )
                    assert s.id_to_index.has_key( id(neighbor_node) ), repr(neighbor_node)
                    output.append( u'''    <item at="%d"/>''' % s.id_to_index[ id(neighbor_node) ] )
                output.append( u'''  </list>''' )
            elif ti.xml_identifier() == "string":
                output.append( u'''  <string id="%d">%s</string>''' % (index,obj) )
            elif ti.xml_identifier() == "dictionary":
                output.append( u'''  <dictionary id="%d">''' % index )
                for (k,v) in obj.items():
                    if type_info( k ).one_per_graph()==False:
                        assert s.graph.get_zone_for_node( k ) == s, "somehow, the key is in another graph?! key: %s" % repr(k)
                    if type_info( v ).one_per_graph()==False:
                        assert s.graph.get_zone_for_node( v ) == s, "somehow, the value is in another graph?! value: %s" % repr(v)
                    output.append( u'''    <bind from="%d" to="%d"/>''' % (s.id_to_index[id(k)],
                                                                           s.id_to_index[id(v)]) )
                output.append( u'''  </dictionary>''' )
            elif ti.xml_identifier() == "reference":
                output.append( u'''  <reference id="%d" url="%s" at="%d"/>''' % (index,obj.url,obj.index) )
        output.append( u'''</zone>''' )
        return u'''\n'''.join( output )

    def read_xml_string( s, xml_string ):
        handler = ZoneHandler( s )
        xml.sax.parseString( xml_string, handler )
        return s
    def read( s, url=None ):
        if url == None:
            url = s.url
        handler = ZoneHandler( s )
        xml.sax.parse( url, handler )
        return s
    def graft_xml_handler_results( s, results ):
        for k in results:
            if s.index_to_object.has_key( k ):
                raise "Can't import XML into nLSD graph; Node %d already assigned." % k
        for (k,v) in results.items():
            s.absorb( v )
            s.number_node( v, k )

class ZoneHandler(xml.sax.handler.ContentHandler):
    def __init__( s, report_to ):
        xml.sax.handler.ContentHandler.__init__( s )
        s.report_to = report_to
    def startDocument( s ):
        s.nodes = {} # int -> node data dictionary
        s.flags = {} # string -> node number
        # always keeping track of
        s.reading_id = None # id# of node immediately reading
        s.read_type = None # name of the element type presently reading
        s.content = None # string content read so far (list of strings)
        # specific to types:
        s.mapping = None # dictionary: mapping so far
        s.items = None # list: items so far
        s.ref = None # container for info
    def startElement( s, name, attrs ):
        s.read_type = name
        s.content = []
        def int_from( attribute_name ):
            return int(attrs[attribute_name])
        if attrs.has_key( "id" ):
            s.reading_id = int_from( "id" )
        if name == "dictionary":
            s.mapping = {}
        elif name == "bind":
            from_id = int_from("from")
            to_id = int_from("to") 
            s.mapping[ from_id ] = to_id
        elif name == "list":
            s.items = []
        elif name == "item":
            s.items.append( int_from("at") )
        elif name == "reference":
            to_url = attrs[ "url" ]
            try:
                to_id = int_from( "at" )
            except ValueError:
                # flag reference, should a string
                to_id = attrs[ "at" ]
            s.ref = s.report_to.get_graph().ref( to_url, to_id )
        elif name == "flag":
            s.flags[ attrs["name"] ]=int_from("at")
    def characters( s, content ):
        if type( s.content ) == type([]):
            s.content.append( content )
    def endElement( s, name ):
        if type( s.content ) == type( [] ):
            content = u"".join(s.content)
            s.content = None
        if name == "dictionary":
            s.nodes[ s.reading_id ] = s.mapping
            s.reading_id = None
            s.mapping = None
        elif name == "list":
            s.nodes[ s.reading_id ] = s.items
            s.reading_id = None
            s.items = None
        elif name == "string":
            s.nodes[ s.reading_id ] = content
        elif name == "integer":
            s.nodes[ s.reading_id ] = int(content)
        elif name == "float":
            s.nodes[ s.reading_id ] = float(content)
        elif name == "reference":
            s.nodes[ s.reading_id ] = s.ref
    def endDocument( s ):
##        import pprint
##        print "----- Nodes as read -----"
##        pprint.pprint( s.nodes )
        # build frame for new mapping
        nodes2 = {}
        for node_id in s.nodes:
            if type( s.nodes[node_id] ) == type( {} ):
                nodes2[ node_id ] = {}
            elif type( s.nodes[node_id] ) == type( [] ):
                nodes2[ node_id ] = []
            else:
                # ints, floats, and strings just keep their value
                nodes2[ node_id ] = s.nodes[node_id]
##        print "----- Framed Nodes -----"
##        pprint.pprint( nodes2 )
        # fill it in
        for node_id in s.nodes:
            old_value = s.nodes[ node_id ]
            if type( old_value ) == type( {} ):
                for k in old_value:
                    new_key = nodes2[ k ]
                    new_val = nodes2[ old_value[k] ]
                    nodes2[node_id][ new_key ] = new_val
            elif type( old_value ) == type( [] ):
                nodes2[node_id].extend( [nodes2[x] for x in old_value] )
##        print "----- Linked Nodes -----"
##        pprint.pprint( nodes2 )
##        pprint.pprint( s.flags )
        s.report_to.graft_xml_handler_results( nodes2 )
