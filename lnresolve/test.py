"""Test Local Names XML-RPC Server.

Tests don't run on an actual XML-RPC query server; Rather, they run on
the module that xrserver.py or xrcgi.py would publish. This demonstrates
an interesting advantage of xrserver.py and xrcgi.py: You can "test the
server" without actually running the server.

The lnxrqs's default store is overridden. In it's place, a Store that
serves two locally defined namespaces. The namespace description at
"http://example.com/" is the basic_text, and the namespace description
at "http://example.net/" is the neighbor_text.

DOC
"""

import unittest

import lncore
import lnxrqs


basic_text = u"""
X "VERSION" "1.2"
LN "foo" "http://example.com/"
LN "bar" "http://example.com/"
X "FINAL" "http://example.com/$NAME"
NS "neighbor" "http://example.net/"
PATTERN "pat" "http://example.com/$ARG1/$ARG2/"
"""

'''Basic namespace description for use in simple tests.'''

neighbor_text = u"""
X "VERSION" "1.2"
LN "baz boz" "http://example.net/bazboz/"
"""

'''Neighbor namespace description for testing namespace links.'''


def return_basic_namespaces(url):
    """Simple namespace builder, used during tests.
    
    Always return basic_text.
    
    Why? Because I do most of my testing in the bus, without access
    to the Internet. So I need a url-to-text builder that doesn't
    require Internet access. Hence this function. It pretends to be
    the Internet, returning text in response to url requests. In
    this case, it always returns basic_text.
    """
    if url == "http://example.net/":
        return neighbor_text
    return basic_text


class LookupTest(unittest.TestCase):
    
    """Test query server lookup function.
    
    DOC
    
    DOC
    """
    
    L = [("foo", "http://example.com/"),
         ("bar", "http://example.com/"),
         ("foo ", "http://example.com/"),
         (" bar ", "http://example.com/"),
         ("baz boz", "http://example.net/bazboz/")]
    
    def testBasicList(self):
        """Perform lookups found in basic test list."""
        for (name, should_result) in LookupTest.L:
            result = lnxrqs.lookup("http://example.com/", name)
            assert result == (0, should_result), (name, result)


class FindTest(unittest.TestCase):
    
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
            result = lnxrqs.find("http://example.com/", find_path,
                                 record_type, "traditional")
            assert result == (0, should_result), (find_path, result)

    def testManyList(self):
        """Perform all lookups in basic test list at once."""
        mini_list = [(x,y,z) for (x,y,z) in FindTest.L if y == "LN"]
        queries = [x for (x,y,z) in mini_list]
        should_results = [(0, z) for (x,y,z) in mini_list]
        results = lnxrqs.find_many("http://example.com/", queries,
                                   "LN", "traditional")
        assert results == should_results, (results, should_results)


if __name__ == "__main__":
    unittest.main() # run all tests

