import unittest
import localnames

TAORIVER_URL = "http://taoriver.net/"
FRESHMEAT_URL = "http://freshmeat.net/"
TEST_NAMESPACE = "http://taoriver.net/data/namespaces/test/index.txt"

class SimpleLinkTestCase(unittest.TestCase):
    def setUp(s):
        s.link = localnames.Link( TAORIVER_URL,"taoriver")
    def tearDown(s):
        pass
    def testGetUrl(s):
        assert s.link.get_url() == TAORIVER_URL, "link init-retrieve URL cycle not working"
    def testGetNames(s):
        assert s.link.get_names() == ("taoriver",), "link init-retrieve names cycle not working"        
    def testGetCanonicalName(s):
        assert s.link.get_canonical_name() == "taoriver", "link init-retrieve canonical name cycle not working"

class ManyNamesLinkTestCase(unittest.TestCase):
    def setUp(s):
        s.link = localnames.Link( TAORIVER_URL,"TaoRiver")
        s.link.add_name( "taoriver" )
    def tearDown(s):
        pass
    def testGetUrl(s):
        assert s.link.get_url() == TAORIVER_URL, "link init-add-retrieve URL cycle not working"
    def testGetNames(s):
        assert s.link.get_names() == ("TaoRiver","taoriver"), "link init-add-retrieve names cycle not working"
    def testGetCanonicalNames(s):
        assert s.link.get_canonical_name() == "TaoRiver", "link init-add-retrieve canonical name cycle not working"

class RemoveNameLinkTestCase(unittest.TestCase):
    def setUp(s):
        s.link = localnames.Link( TAORIVER_URL,"TaoRiver")
        s.link.add_name( "foo" )
        s.link.add_name( "taoriver" )
        s.link.remove_name( "foo" )
    def tearDown(s):
        pass
    def testGetUrl(s):
        assert s.link.get_url() == TAORIVER_URL, "link init-add-remove-retrieve URL cycle not working"
    def testGetNames(s):
        assert s.link.get_names() == ("TaoRiver","taoriver"), "link init-add-remove-retrieve names cycle not working"
    def testGetCanonicalNames(s):
        assert s.link.get_canonical_name() == "TaoRiver", "link init-add-remove-retrieve canonical name cycle not working"

link_testsuite = unittest.TestSuite(
    [ unittest.makeSuite( x, "test"  )
      for x in [SimpleLinkTestCase,
                ManyNamesLinkTestCase,
                RemoveNameLinkTestCase] ] )

class SimpleLinkStoreTestCase( unittest.TestCase ):
    def setUp(s):
        s.store = localnames.LinkStore()
        s.store.bind( "TaoRiver", TAORIVER_URL )
        s.store.bind( "taoriver", TAORIVER_URL )
    def tearDown(s):
        pass
    def testLookup(s):
        assert s.store.lookup( "TaoRiver" ) == TAORIVER_URL, "can't lookup TaoRiver"
        assert s.store.lookup( "taoriver" ) == TAORIVER_URL, "can't lookup taoriver"
    def testLookupByOtherCase(s):
        assert s.store.lookup( "TAORIVER" ) == TAORIVER_URL, "can't lookup with alternative case"
        assert s.store.lookup( "TaOrIvEr" ) == TAORIVER_URL, "can't lookup with alternative case"
    def testBadLookup(s):
        assert s.store.lookup( "foo" ) == None, "can't perform bad lookup"
    def testCanonicalNames(s):
        assert s.store.canonical_names() == [ "TaoRiver" ], "doesn't report canonical names right"
    def testCanonicalNameForName(s):
        assert s.store.canonical_name_for_name( "taoriver" ) == "TaoRiver", "doesn't retrieve canonical names by other names"
    def testCanonicalNameForUrl(s):
        assert s.store.canonical_name_for_url( TAORIVER_URL ) == "TaoRiver", "doesn't retrieve canonical name by url right"

class NameSpaceTestCase( unittest.TestCase ):
    def setUp(s):
        s.ns = localnames.NameSpace( TEST_NAMESPACE )
    def tearDown(s):
        pass
    def testLookupName(s):
        assert s.ns.lookup_name( "TaoRiver" ) == "http://taoriver.net/", "TaoRiver doesn't resolve to http://taoriver.net/"
        assert s.ns.lookup_name( "taoriver" ) == "http://taoriver.net/", "taoriver (diff case) doesn't resolve to http://taoriver.net/"
    def testLookupSpace(s):
        assert s.ns.lookup_space( "LionKimbro" ) == "http://lion.taoriver.net/localnames.txt", "LionKimbro doesn't resolve to http://lion.taoriver.net/localnames.txt"
        assert s.ns.lookup_space( "lionkimbro" ) == "http://lion.taoriver.net/localnames.txt", "lionkimbro (different case) doesn't resolve to http://lion.taoriver.net/localnames.txt"
    
    
if __name__=="__main__":
    unittest.main()


