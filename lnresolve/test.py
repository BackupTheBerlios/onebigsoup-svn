"""Test Local Names XML-RPC Server.

Running this test requires a particular server configuration.

You need:
* $SVN/other/testserve directory, where $SVN is a onebigsoup project's
  subversion repository checkout.
* run the testserve.py script, serving on port 8000.
* run the resolver in here, on port 8080.
** I recommend using "xrserve.py --server=localhost --port=8080".

For tests of the lncore that don't require the XML-RPC server, use
$SVN/lncore/test.py. That should pretty thoroughly check out the basic
Local Names functionality.

This testing code is for testing network circuits. It doesn't test
foreign code out in the wild, yet (2005-11-17,) but it
should. (TODO:CHECK.)

DOC
"""

import unittest

import xmlrpclib


URL_BASE = "http://localhost:8000"
LNXRQUERYS_URL = "http://localhost:8080/"

EXAMPLE_COM = URL_BASE + "/example.com.txt"


class UsesLNXRQueryS(unittest.TestCase):
    
    """DOC
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        """DOC"""
        self.server = xmlrpclib.ServerProxy(LNXRQUERYS_URL)


class LookupTest(UsesLNXRQueryS):
    
    """Test query server lookup function.
    
    DOC
    
    DOC
    """
    
    L = [("foo", "http://example.com/"),
         ("bar", "http://example.com/"),
         ("foo ", "http://example.com/"),  # approximate lookup
         (" bar ", "http://example.com/"),
         ("baz boz", "http://example.net/bazboz/")]
    
    TEST_URL = URL_BASE + "/example.com.txt"
    
    def testBasicList(self):
        """Perform lookups found in basic test list."""
        for (name, should_result) in LookupTest.L:
            result = self.server.lnquery.lookup(EXAMPLE_COM, name)
            assert result == [0, should_result], (name, result)


class FindTest(UsesLNXRQueryS):
    
    """Test query server find function.
    
    DOC
    
    DOC
    """
    
    L = [(["foo"], "LN", "http://example.com/"),
         (["bar"], "LN", "http://example.com/"),
         (["foo "], "LN", "http://example.com/"),
         ([" bar "], "LN", "http://example.com/"),
         (["baz boz"], "LN", "http://example.net/bazboz/"),
         (["bleep"], "LN", "http://example.com/bleep"),
         (["FINAL"], "X", ["http://example.com/$NAME"]),
         (["pat", "a", "b"], "LN", "http://example.com/a/b/"),]
    
    def testBasicList(self):
        """Perform lookups found in basic test list."""
        for (find_path, record_type, should_result) in FindTest.L:
            result = self.server.lnquery.find(EXAMPLE_COM, find_path,
                                              record_type,
                                              "traditional")
            assert result == [0, should_result], (find_path, result)
    
    def testManyList(self):
        """Perform all lookups in basic test list at once."""
        mini_list = [(x,y,z) for (x,y,z) in FindTest.L if y == "LN"]
        queries = [x for (x,y,z) in mini_list]
        should_results = [[0, z] for (x,y,z) in mini_list]
        results = self.server.lnquery.find_many(EXAMPLE_COM, queries,
                                                "LN", "traditional")
        assert results == should_results, (results, should_results)


if __name__ == "__main__":
    unittest.main() # run all tests

