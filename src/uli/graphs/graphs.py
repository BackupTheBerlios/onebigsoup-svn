
import pickle
import os



class Graph:
    def __init__(s, pickle_filename, neato_filename, png_filename ):
        s.pickle = GraphPickle( s, pickle_filename )
        s.to_neato = GraphToNeato( s, neato_filename )
        s.to_png = GraphToPng( s, png_filename )
        s.nodes = GraphNodes( s )
        s.connections = GraphConnections( s )
        s.summary = GraphSummary( s )
        
        s.pickle.load()

    def event_savetodict( s, d ):
        s.nodes.event_savetodict( d )
        s.connections.event_savetodict( d )
        s.summary.event_savetodict( d )
    def event_loadfromdict( s, d ):
        s.nodes.event_loadfromdict( d )
        s.connections.event_loadfromdict( d )
        s.summary.event_loadfromdict( d )
    def event_clear( s ):
        s.nodes.event_clear()
        s.connections.event_clear()
        s.summary.event_clear()

class GraphPickle:
    def __init__( s, graph, pickle_filename ):
        s.graph = graph
        s.filename = pickle_filename
    def load(s):
        try:
            d = pickle.load( open(s.filename) )
            s.graph.event_loadfromdict( d )
        except IOError:
            pass
    def save(s):
        d = {}
        s.graph.event_savetodict( d )
        pickle.dump( d, open(s.filename,"w") )

class GraphNodes:
    def __init__( s, graph ):
        s.graph = graph
        s.nodes = []
        s.next_node_id = 0
    def event_loadfromdict( s, d ):
        s.nodes = d[ "nodes" ]
        s.next_node_id = d[ "next_node_id" ]
    def event_savetodict( s, d ):
        d[ "nodes" ] = s.nodes
        d[ "next_node_id"] = s.next_node_id
    def event_clear( s ):
        s.nodes = []
        s.next_node_id = 0
    def create_node( s, title=None ):
        node = GraphNode( s.graph )
        if title:
            node.set_title( title )
        node.set_id( s.next_node_id )
        s.next_node_id = s.next_node_id+1
        s.nodes.append( node )
        return node
    def find_node( s, id_or_title ):
        for node in s.nodes:
            if type( id_or_title ) == type( 42 ):
                if node.get_id() == id_or_title:
                    return node
            elif type( id_or_title ) == type( "string" ):
                if node.get_title() == id_or_title:
                    return node
        return None
    def get_nodes( s ):
        return s.nodes

class GraphNode:
    def __init__( s, graph ):
        s.graph = graph
        
        s.title = "(untitled)"
        s.id = -1
        s.color = "black"
        
    def set_id( s, id ):
        s.id = id
    def get_id( s ):
        return s.id
    
    def set_title( s, title ):
        s.title = title
    def get_title( s ):
        return s.title

    def set_color( s, color ):
        s.color = color
    def get_color( s ):
        return s.color

class GraphConnections:
    def __init__( s, graph ):
        s.graph = graph
        s.connections = []
    def event_loadfromdict( s, d ):
        s.connections = d[ "connections" ]
    def event_savetodict( s, d ):
        d[ "connections" ] = s.connections
    def event_clear( s ):
        s.connections = []
    def create_connection( s, node_a, node_b ):
        connection = GraphConnection( s.graph )
        connection.set_nodes( node_a, node_b )
        s.connections.append( connection )
        return connection
    def destroy_connection( s, node_a, node_b ):
        connection = s.find_connection( node_a, node_b )
        if connection:
            s.connections.remove( connection )
            return True
        return False
    def find_connection( s, node_a, node_b ):
        for connection in s.connections:
            (a,b) = connection.get_nodes()
            if a==node_a and b==node_b:
                return connection
            if a==node_b and b==node_a:
                return connection
        return None
    def get_connections( s ):
        return s.connections
    def scale_lengths( s, factor ):
        for conn in s.connections:
            conn.set_length( conn.get_length() * factor )

class GraphConnection:
    def __init__( s, graph ):
        s.graph = graph
        s.a = -1
        s.b = -1
        s.length = 1.0
        s.bold = False
        s.color = "black"
    def set_nodes( s, node_a, node_b ):
        s.a = node_a.get_id()
        s.b = node_b.get_id()
    def get_nodes( s ):
        return ( s.graph.nodes.find_node( s.a ),
                 s.graph.nodes.find_node( s.b ) )
    def set_length( s, length ):
        s.length = length
    def get_length( s ):
        return s.length
    
    def set_bold( s, bold=True ):
        s.bold=bold
    def get_bold( s ):
        return s.bold
    def set_color( s, color ):
        s.color=color
    def get_color( s ):
        return s.color

class GraphSummary:
    def __init__( s, graph ):
        s.graph = graph
        s.title = "(no title given)"
    def event_loadfromdict( s, d ):
        s.title = d[ "title" ]
    def event_savetodict( s, d ):
        d[ "title" ] = s.title
    def event_clear( s ):
        s.title = "(no title given)"
    def set_title( s, title ):
        s.title = title
    def get_title( s ):
        return s.title

class GraphToNeato:
    def __init__( s, graph, neato_filename ):
        s.graph = graph
        s.filename = neato_filename
    def write_to( s, file_obj ):
        file_obj.write( "graph G {\n" )
        for node in s.graph.nodes.get_nodes():
            file_obj.write( '    "%s" [color=%s];\n' % (node.get_title(),node.get_color()) )
        for connection in s.graph.connections.get_connections():
            a,b = connection.get_nodes()
            length = connection.get_length()
            color = connection.get_color()
            (a,b) = (a.get_title(),b.get_title())
            file_obj.write( '    "%s" -- "%s" [color=%s, len=%f %s]\n' % (a,b,color, length, {False:"",True:", style=bold"}[connection.get_bold()]) )
        file_obj.write( "}\n" )
    def write( s, filename=None ):
        if filename==None:
            filename = s.filename
        file = open( filename, "w" )
        s.write_to( open( filename, "w" ) )

class GraphToPng:
    def __init__( s, graph, png_filename ):
        s.graph = graph
        s.filename = png_filename
    def write( s, filename=None ):
        if filename==None:
            filename = s.filename

        # neato_file --> neato -Tpng --> png_file
        (pipe_write,pipe_read,pipe_err) = os.popen3( "neato -Tpng" )

        # write in the neato_file
        s.graph.to_neato.write_to( pipe_write )
        pipe_write.close()

        # write out the png_file
        png_data = pipe_read.read()
        open( filename, "w" ).write( png_data )


