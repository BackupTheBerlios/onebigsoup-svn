#!/usr/bin/env python2.3
"""
graph drawing ULI service
"""

import graphs
import uli_graphs
import cgi



# global settings
PICKLE_FILENAME = "graph.p"
GRAPH_NEATO = "graph.neato"
GRAPH_PNG = "graph.png"



if __name__ == "__main__":
    graph = graphs.Graph( PICKLE_FILENAME, GRAPH_NEATO, GRAPH_PNG )
    uli = uli_graphs.Uli( graph )
    uli_response = uli_graphs.BasicHttpUliResponse( uli )

    form = cgi.FieldStorage()

    if form.has_key( "ULI" ):
        uli_response.respond_http( form["ULI"].value )
    else:
        print "Content-type: text/html"
        print
        print "<html><head><title>ULI Server - Graphs</title></head>"
	print "<body>"
	print "<h3> %s </h3>" % graph.summary.get_title()
	print "<p>"
	print '<img src="graph.png"/>'
	print "</p>"
	print "</body>"
	print "</html>"


