import graphs



LENGTH_SCALING_FACTOR = 1.0



class Uli:
    def __init__( s, graph ):
        s.graph = graph
    def uli( s, line ):
        msg = "(I don't know how to handle '%s')" % line
        
        tokens = []
        for (n,cut) in enumerate( line.split('"') ):
            if n%2==0:
                tokens.extend( cut.split() ) # not in quotes- individual tokens
            else:
                tokens.append( cut ) # in quotes, so it's a full token

        if line == "ping": msg="pong"
        elif line == "whoareyou": msg="Graphs Construction ULI Port"
        elif line == "frametype": msg="Custom HTTP-CGI ULI Port"
        elif line == "whoareyou-data": msg="not implemented"
        elif line == "help": msg="commands: clear, (node) -- (node), (node) == (node), (node) -X- (node), scale-lengths (factor- ex:1.2), color (node) red/green/blue/black, can optionally specify color after connection lines"
        elif line == "clear":
            s.graph.event_clear()
            msg="clear!"
        elif line.startswith( "title" ):
            title = line.split(None,1)[1]
            s.graph.summary.set_title( title )
            msg="graph title: %s" % title
        elif len(tokens)==2 and tokens[0] == "scale-lengths":
            factor = float(tokens[1])
            s.graph.connections.scale_lengths( factor )
            msg="scaled by %f" % factor
        elif line.startswith( "node" ):
            node_title = line.split(None,1)[1]
            s.graph.nodes.create_node( node_title )
            msg="new node: %s" % node_title
        elif len(tokens)==3 and tokens[0] == "color" and tokens[2].lower() in ["red","green","blue","black"]:
            node = s.graph.nodes.find_node( tokens[1] )
            if not node:
                msg = "no such node: %s" % tokens[1]
            else:
                node.set_color( tokens[2].lower() )
                msg="set color: %s" % tokens[2].lower()
        elif len(tokens)==3 and tokens[1] == "-X-":
            node_a_title = tokens[0]
            node_b_title = tokens[2]
            node_a = s.graph.nodes.find_node( node_a_title )
            node_b = s.graph.nodes.find_node( node_b_title )
            if node_a and node_b and s.graph.connections.destroy_connection( node_a, node_b ):
                msg = "disconnected"
            else:
                if (not node_a) and (not node_b): msg = "couldn't find node %s or node %s" % (node_a.get_title(),node_b.get_title())
                elif not node_a: msg = "couldn't find node %s" % node_a.get_title()
                elif not node_b: msg = "couldn't find node %s" % node_b.get_title()
                else: msg = "couldn't find connection between node %s and node %s" % (node_a.get_title(),node_b.get_title())
        elif len(tokens)>=3 and (tokens[1].startswith("-") or tokens[1].startswith("=")):
            node_a_title = tokens[0]
            node_b_title = tokens[2]
            distance = len(tokens[1])*LENGTH_SCALING_FACTOR
            node_a = s.graph.nodes.find_node( node_a_title ) or s.graph.nodes.create_node( node_a_title )
            node_b = s.graph.nodes.find_node( node_b_title ) or s.graph.nodes.create_node( node_b_title )
            connection=s.graph.connections.create_connection( node_a, node_b )
            connection.set_length( distance )
            msg = "new connection: %s to %s, length %f" % (node_a_title, node_b_title, distance)
            if tokens[1].startswith("="):
                connection.set_bold()
                msg = msg + " [bold]"
            if len(tokens)>3:
                if tokens[3] in ["red","green","blue","black"]:
                    connection.set_color( tokens[3] )
                    msg = msg + " [%s]" % tokens[3]
        s.graph.pickle.save()
        s.graph.to_neato.write()
        s.graph.to_png.write()
        return msg

class BasicHttpUliResponse:
    """
    (presently unused)
    """
    def __init__( s, uli ):
        s.uli = uli
    def respond_http( s, line ):
        result = s.uli.uli( line )
        print "Content-type: text/html"
        print
        print result

if __name__ == "__main__":
    graph = graphs.Graph( "graph.p", "graph.neato", "graph.png" )
    uli = Uli( graph )
    print uli.uli( 'clear' )
    print uli.uli( 'A -- Blue' )
    print uli.uli( 'A ---- B' )
    print uli.uli( 'A -- C' )
    print uli.uli( 'B --- C' )
    print uli.uli( 'color Blue blue' )
    print uli.uli( 'color C red' )
    print uli.uli( 'color B green' )


