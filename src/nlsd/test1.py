from graph import *

gs = GraphStore()
g = gs.new_graph( "foo" )

g.accept( [ Ref( "bar" ),
            "hello",
            "world!", ] )

gstring1 = g.serialize()

# ---

gs = GraphStore()
g = gs.new_graph( "bar" )

g.accept( [ "the",
            "river",
            "of",
            "hope",
            Ref( "foo" ), ] )

gstring2 = g.serialize()

# ---

gs = GraphStore()
foo = gs.create_graph_by_string( "foo", gstring1 )
bar = gs.create_graph_by_string( "bar", gstring2 )

x = foo.start()

print gstring1
print gstring2

print
print
print "---AND NOW, OVER THE NETWORK---"
print
print

gs = GraphStore()
bar = gs.graph_from_url( "http://www.speakeasy.org/~lion/data/bar.txt" )
gs.resolve_all_refs_recursively()
#foo = gs.graph_from_url( "http://taoriver.net/tmp/foo.txt" )
print bar.start()
