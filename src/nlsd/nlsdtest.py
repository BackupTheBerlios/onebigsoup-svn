
#
# LEO:
# WORK IN PROGRESS:
#
#    SEARCH DOCUMENTS FOR "LEO", THEY TELL YOU WHAT NEEDS
#    TO BE DONE TO FINISH REF--GRAPH TIES.
#


import unittest

import nlsd # module testing

class CountCalls:
    def __init__( s ):
        s.calls = 0
    def __call__( s, *args ):
        s.calls = s.calls + 1
        return s.calls

class TestBasics(unittest.TestCase):
    def testListNeighbors(s):
        L=[1,2,3]
        ti=nlsd.type_info(L)
        assert len(ti.get_neighbors()) == 3, "List doesn't have 3 neighbors."
        assert ti.get_neighbors() == [1,2,3], "List doesn't return it's contents as neighbors."    

class TestVisitation(unittest.TestCase):
    def setUp(s):
        s.G = nlsd.Graph()
        s.z = nlsd.Zone( "lion", s.G )
        s.L = [1,2,3]
        s.L.append( s.L )
    def tearDown(s):
        pass
    def testVisitation(s):
        counter = CountCalls()
        s.G.visit( s.L, counter, nlsd.GO_EVERYWHERE )
        num_calls = counter()-1
        assert num_calls == 4, "Didn't talk to 4 items, talked to %d items" % num_calls

class TestRef(unittest.TestCase):
    def setUp(s):
        s.r1=nlsd.Ref(None,"foo",1)
        s.r2=nlsd.Ref(None,"foo",1)
        s.r3=nlsd.Ref(None,"bar",5)
    def tearDown(s):
        pass
    def testRefCompareEqual(s):
        assert s.r1==s.r2, "equal refs don't appear so"
    def testRefCompareDifferent(s):
        assert s.r1!=s.r3, "unequal refs don't appear so"

class TestReferences(unittest.TestCase):
    def setUp(s):
        s.G = nlsd.Graph()
        s.z = nlsd.Zone( "s.z", s.G )
        s.L = [1,2,3,s.G.ref( "s.y", 2 )]
        s.z.absorb( s.L )
        s.y = nlsd.Zone( "s.y", s.G )
        s.K = ["a","b","c","d","e","f"]
        s.y.absorb( s.K )
        s.y.number_node( s.K[2], 2 ) # "s.y #2" --> "c"
        s.z.number()
        s.y.number()
    def tearDown(s):
        pass
    def testReplaceListRef(s):
        L=[1,2,3]
        ti=nlsd.type_info(L)
        ti.replace_ref( 2, "bunny" )
        assert L[1] == "bunny", "not replacing entries within lists"
    def testResolveRef(s):
	    # LEO:
	    # WORK IN PROGRESS:
	    # it looks like the reference isn't being
	    # found in s.z
        L=[1,2,s.G.ref( "s.y", 2 ),4]
	s.z.absorb( L )
        L[2].resolve()
        assert L[2] == "c", "resolving single Ref from Ref fails"
    def testReplaceDictionaryRef(s):
        D={"one":1,"bad-two":2,"three":"bad-3"}
        ti=nlsd.type_info( D )
        ti.replace_ref( "bad-two", "two" )
        ti.replace_ref( "bad-3", 3 )
        assert D.get("two") == 2, "not replacing keys within dicts"
        assert D.get("three") == 3, "not replacing values within dicts"
    def testFindLinkTarget(s):
        target = s.G.find_ref_target( s.G.ref( "s.y", 2 ) )
        assert s.y[2] == s.K[2], "y[2] is pointing to the wrong thing; can't resolve ref"
    def testLinkOne(s):
        s.G.replace_refs_for( s.L )
        assert s.L[3] == s.K[2], "Linking an individual Ref isn't working."

class TestPlaceReferences(unittest.TestCase):
    def setUp(s):
        s.G = nlsd.Graph()
        s.y = nlsd.Zone( "s.y", s.G )
        s.z = nlsd.Zone( "s.z", s.G )
	s.y[0] = [ "list", "in", "y" ]
	s.z[0] = [ "list", "in", "z", s.y[0] ]
	s.y[0].append( s.z[0] )
        s.y.number()
        s.z.number()
        s.G.replace_refs()
    def testNativeListInfo(s):
	L=[1,2,3, s.y[0]]
        ti=nlsd.NativeListInfo( L )
        ti.place_ref( s.G, s.y[0] )
        # LEO:
        # WORK IN PROGRESS:
        # make this work,
        # by passing Graph (s.G) to place_ref,
        # and comparing with s.G based graph-
        #
        # also, from this point on,
        # replace all Ref use with Ref( GRAPH, neighbor_node )
        assert L[3] == s.G.ref( "s.y", 0 )
    def testPlaceOneReference(s):
        s.G.place_refs_for( s.y[0] )
        assert s.y[0][3] == s.G.ref("s.z",0), "Couldn't place Ref."
    def testPlaceManyReferences(s):
        s.G.place_refs()
        assert s.y[0][3] == s.G.ref("s.z",0), "Couldn't place Ref."
        assert s.z[0][3] == s.G.ref("s.y",0), "Couldn't place Ref."

class TestReferenceRetrieval(unittest.TestCase):
    def setUp(s):
        s.G = nlsd.Graph()
        s.front = nlsd.Zone( "file:front.xml", s.G )
    def testReadFromUrl(s):
        s.front.read()
        assert s.front[0]["dirs"]["north"] == s.G.ref( "file:forest.xml", 0 ), "not reading from front.xml correctly"
    def testResolveUrls(s):
        s.front.read()
        s.front.replace_refs( retrieve_from_url=True )
        assert s.front[0]["dirs"]["north"]["desc"] == "in a forest"

class TestAssimilation(unittest.TestCase):
    def setUp(s):
        s.G = nlsd.Graph()
        s.z = nlsd.Zone( "s.z", s.G )
        s.L = [1,2,3]
        s.L.append( s.L )
        s.z.absorb( s.L )
    def tearDown(s):
        pass
    def testLengthIdToObject(s):
        assert len( s.z.id_to_object ) == 4, "Not four objects in id_to_object."
    def testLengthZone(s):
        assert len( s.z ) == 4, "Not four objects in Zone z."
    def testNumberOneNode(s):
        s.z.number_node( s.L, 0 )
        assert s.z[0] == s.L, "Can't number just L to #0."
    def testNumberTwoNodes(s):
        s.z.number_node( s.L, 0 )
        s.z.number_node( s.L[0], 0 )
        assert s.z[0] == s.L, "Can't number L to 0."
        assert s.z[1] == 1, "Can't number L[0] to 1."
    def testNumbering(s):
        s.z.number()
        seen = []
        seen.append( s.z[0] )
        seen.append( s.z[1] )
        seen.append( s.z[2] )
        seen.append( s.z[3] )
        assert s.L in seen, "L not numbered."
        assert 1 in seen, "1 not numbered."
        assert 2 in seen, "2 not numbered."
        assert 3 in seen, "3 not numbered."
    def testOnePerGraph(s):
        """
        Make sure each graph get's it's own copy of
        constants like 1,2,3.
        """
        y = nlsd.Zone( "kitty", s.G )
        y.absorb( [1,2,3] )
        assert len(y)==4, "additional graph has only %d items" % len(y)
    def testNoRenumbering(s):
        s.z.number()
        assert s.z.number_node( s.z[0] ) == 0, "renumbering!"
    def testNoGoingIntoOtherZones(s):
        y=nlsd.Zone( "y", s.G )
        y[0] = ["a","b","c"]
        y.number()

        s.z[0] = s.L
        s.z.number()
        s.z[0].append( y[0] )
        s.z.absorb()
        s.z.number()
        
        assert not (y[0] in s.z), "zones are absorbing other zones"

class GeneralScenarios(unittest.TestCase):
    def setUp(s):
        s.lion = nlsd.Zone( "lion" )
        s.alex = nlsd.Zone( "alex", s.lion.get_graph() )
        s.lion[0] = { "name": "Lion Kimbro",
                      "friends": [] }
        s.alex[0] = { "name": "Alex ---------",
                      "friends": [] }
        s.lion.number()
        s.alex.number()

        s.lion[0]["friends"].append( s.alex[0] )
        s.alex[0]["friends"].append( s.lion[0] )
    def tearDown(s):
        pass
    def testUnRef(s):
        s.lion.get_graph().place_refs()
        assert s.lion[0]["friends"][0] == s.lion.get_graph().ref( "alex", 0 )
        assert s.alex[0]["friends"][0] == s.lion.get_graph().ref( "lion", 0 )
    def testXml(s):
##        print "visually inspect:"
##        print s.lion.xml()
##        s.lion.stat()
##        print "visually inspect:"
##        print s.alex.xml()
##        s.alex.stat()
        # raise an exception on failure
        pass

class TestReadXml(unittest.TestCase):
    def setUp(s):
        s.G = nlsd.Graph()
        s.z = nlsd.Zone( "s.z", s.G )
        s.z.absorb( "unnumbered" )
        s.z.absorb( "junk" )
        s.z.absorb( "data" )
    def tearDown(s):
        pass
    def testInteger(s):
        xml_string="""<?xml version="1.0" standalone="yes"?>

<zone>
  <integer id="0">42</integer>
</zone>"""
        s.z.read_xml_string( xml_string )
        assert s.z[0] == 42, "Not reading integers by XML."
    def testFloat(s):
        xml_string="""<?xml version="1.0" standalone="yes"?>

<zone>
  <float id="0">42.0</float>
</zone>"""
        s.z.read_xml_string( xml_string )
        assert s.z[0] == 42.0, "Not reading floats by XML."
    def testList(s):
        xml_string="""<?xml version="1.0" standalone="yes"?>

<zone>
  <list id="0">
    <item at="1"/>
    <item at="2"/>
    <item at="3"/>
  </list>
  <integer id="1">1</integer>
  <integer id="2">2</integer>
  <integer id="3">3</integer>
</zone>"""
        s.z.read_xml_string( xml_string )
        assert s.z[0] == [1,2,3], "Not reading lists by XML."
    def testString(s):
        xml_string="""<?xml version="1.0" standalone="yes"?>

<zone>
  <string id="0">foo bar</string>
</zone>"""
        s.z.read_xml_string( xml_string )
        assert s.z[0] == "foo bar", "Not reading strings by XML."
    def testDictionary(s):
        xml_string="""<?xml version="1.0" standalone="yes"?>

<zone>
  <dictionary id="0">
    <bind from="1" to="2"/>
    <bind from="3" to="4"/>
  </dictionary>
  <string id="1">one</string>
  <integer id="2">2</integer>
  <string id="3">three</string>
  <integer id="4">4</integer>
</zone>"""
        s.z.read_xml_string( xml_string )
        assert s.z[0] == {"one":2,"three":4}, "Not reading dictionaries by XML."
    def testRef(s):
        xml_string="""<?xml version="1.0" standalone="yes"?>

<zone>
  <reference id="0" url="foo" at="start"/>
</zone>"""
        s.z.read_xml_string( xml_string )
        assert s.z[0] == s.G.ref( "foo", "start" ), "Not reading dictionaries by XML."

    def testReadSimpleXml(s):
        xml="""<?xml version="1.0" standalone="yes"?>

<zone>
  <dictionary id="0">
    <bind from="1" to="3"/>
    <bind from="2" to="4"/>
  </dictionary>
  <string id="1">friends</string>
  <string id="2">name</string>
  <list id="3">
    <item at="5"/>
  </list>
  <string id="4">Lion Kimbro</string>
  <reference id="5" url="alex" at="0"/>
</zone>"""
        s.z.read_xml_string( xml )
        assert s.z[0]["name"] == u"Lion Kimbro"
        
    def testReadFromFile(s):
        s.z.url = "file:data.xml"
        s.z.read()
        assert s.z[2]=="Lion Kimbro", "didn't read data from file correctly"

if __name__ == "__main__":
    unittest.main() # run all tests

