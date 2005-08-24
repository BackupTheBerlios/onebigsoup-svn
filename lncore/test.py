"""DOC

DOC

DOC
"""

import unittest

import lncore


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


class QuotationTests(unittest.TestCase):
    
    """Test quoting and unquoting.
    
    DOC
    
    testQuote  -- DOC
    testUnquote  -- DOC
    testStrange  -- DOC
    """
    
    # testQuote & testUnquote share several tests, which we store here.
    
    L = [('foo', '"foo"'),
         ('foo bar', '"foo bar"'),
         ('foo\nbar', '"foo\\nbar"'),
         ('0123456789', '"0123456789"'),
         ('"roborally"', '"\\"roborally\\""')]
    
    def testQuote(self):
        """Test generic quotes via list."""
        for (first, second) in QuotationTests.L:
            assert lncore.quote(first) == second, (first, second)
    
    def testUnquote(self):
        """Test generic unquotes via list."""
        for (first, second) in QuotationTests.L:
            assert lncore.unquote(second) == first, (first, second)
    
    def testStrange(self):
        """Test cases that are likely to fail in first lncore.
        
        These are tests that should pass, but are harder to code for.
        They are rare, but we eventually want to code to solve them.
        """
        pass


class LineTests(unittest.TestCase):
    
    """Test line recognition.
    
    DOC
    
    testRecordInterpretation  -- test record details
    testLineInterpretation  -- test line types
    """
    
    records = [('LN "foo" "http://example.com/"',
                lncore.LN, "foo", "http://example.com/"),
               ('NS "foo" "http://example.com/"',
                lncore.NS, "foo", "http://example.com/"),
               ('X "foo" "http://example.com/"',
                lncore.X, "foo", "http://example.com/"),
               ('PATTERN "foo" "http://example.com/"',
                lncore.PATTERN, "foo", "http://example.com/"),]
    
    lines = [('LN "foo" "http://example.com/"', lncore.Line.RCD),
             ('# This is a comment."', lncore.Line.CMT),
             ('', lncore.Line.BLK),
             ('An error.', lncore.Line.ERR),]
    
    def testRecordInterpretation(self):
        """Test details of record line interpretation."""
        for (line, record_type, key, value) in LineTests.records:
            line = lncore.Line(line)
            assert line.record_type == record_type
            assert line.key == key
            assert line.value == value
    
    def testLineInterpretation(self):
        """Test that line types are proprely recognized."""
        for (line, line_type) in LineTests.lines:
            line = lncore.Line(line)
            assert line.line_type == line_type


class TokenizingTest(unittest.TestCase):
    
    """DOC
    
    DOC
    
    DOC
    """
    
    results = [(lncore.Line.BLK,
                None, None, None),
               (lncore.Line.RCD,
                lncore.X, "VERSION", "1.2"),
               (lncore.Line.RCD,
                lncore.LN, "foo", "http://example.com/"),
               (lncore.Line.RCD,
                lncore.LN, "bar", "http://example.com/"),
               (lncore.Line.RCD,
                lncore.X, "FINAL", "http://example.com/$NAME"),
               (lncore.Line.RCD,
                lncore.NS, "neighbor", "http://example.net/"),
               (lncore.Line.RCD,
                lncore.PATTERN, "pat",
                "http://example.com/$ARG1/$ARG2/"),
               (lncore.Line.BLK,
                None, None, None),]
    
    def testLines(self):
        """DOC"""
        lines = lncore.text_to_lines(basic_text)
        specs = TokenizingTest.results
        for (line, spec) in zip(lines, specs):
            (line_type, record_type, key, value) = spec
            assert line.line_type == line_type, line.line_type
            assert line.record_type == record_type
            assert line.key == key
            assert line.value == value, spec


class NamespaceTest(unittest.TestCase):
    
    """Test namespace functionality.
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        """Create a namespace to test from the basic text."""
        lines = lncore.text_to_lines(basic_text)
        self.namespace = lncore.lines_to_namespace(lines)
    
    def testConversionFromText(self):
        """Check values in the namespace."""
        assert self.namespace[lncore.LN]["foo"] == "http://example.com/"
        assert self.namespace[lncore.LN]["bar"] == "http://example.com/"
        assert self.namespace[lncore.X]["VERSION"] == ["1.2"]
    
    def testFinal(self):
        """Check that X FINAL replacement works properly."""
        assert self.namespace.final("foo") == "http://example.com/foo"
    
    def testBulletinBoard(self):
        """Check that the bulletin board keeps entries separate."""
        self.namespace.get_bboard("FOO")["foo"] = "AAA"
        self.namespace.get_bboard("BAR")["foo"] = "ZZZ"
        assert self.namespace.get_bboard("FOO")["foo"] == "AAA"


class UrlTemplateTest(unittest.TestCase):
    
    """Test URL templates.
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        """Create simple URL templates."""
        self.pattern = lncore.UrlTemplate("http://example.com/$NAME")
        args_text = "http://example.com/$ARG1/$ARG2/$ARG3"
        self.args_pattern = lncore.UrlTemplate(args_text)
    
    def testNameReplacement(self):
        """DOC"""
        assert self.pattern.replace("foo") == "http://example.com/foo"
    
    def testArgsReplacement(self):
        """DOC"""
        val = self.args_pattern.replace(["foo", "bar", "baz"])
        assert val == "http://example.com/foo/bar/baz"


class TestThatUsesTestStore(unittest.TestCase):

    """Super-class for tests that use the TestStore.

    DOC - children need call setUp if override.

    DOC
    """
    
    def setUp(self):
        """Create simple Store."""
        self.store = lncore.TestStore()
        self.store.bind("http://example.com/", basic_text)
        self.store.bind("http://example.net/", neighbor_text)


class StoreTest(TestThatUsesTestStore):
    
    """Test the test namespace description Store.

    It feels a bit silly to test a test store, and perhaps it is. But
    there are other tests that are going to rely on the TestStore, and I
    want to make sure that it's actually working like I think it does.
    
    DOC
    
    DOC
    """
    
    def testCaching(self):
        """Make sure that the store is caching namespaces."""
        ns1 = self.store("http://example.com/")
        ns1.get_bboard("test")["flag"] = True
        ns2 = self.store("http://example.com/")
        assert ns1.get_bboard("test")["flag"] == True

    def testCacheList(self):
        """Make sure that get_cache_list works."""
        correct = [("", "http://example.com/", 1000),
                   ("", "http://example.net/", 1000)]
        correct2 = [("", "http://example.net/", 1000),
                    ("", "http://example.com/", 1000)]
        result = self.store.get_cache_list()
        assert result == correct or result == correct2, result


class TraditionalStyleTest(TestThatUsesTestStore):
    
    """Test Traditional Style resolution.
    
    DOC
    
    DOC: JUST THOUGHTS; REWORK OR DELETE THEM LATER:
    We want to make sure that:
    * It resolves a correctly spelled name.
    * It resolves a closely spelled name.
    * It resolves a name found in a neighboring namespace.
    * It resolves a closely spelled name in a neighboring namespace.
    * That it can namespace hop.
    * That PATTERNs are resolved.
    * That X "FINAL" works.
    
    DOC
    """
    
    L = [("LN", "foo", "http://example.com/"),
         ("LN", "bar", "http://example.com/"),
         ("LN", "foos", "http://example.com/"),
         ("LN", "baz boz", "http://example.net/bazboz/"),
         ("LN", "bazboz", "http://example.net/bazboz/"),
         ("LN", ["neighbor", "baz boz"], "http://example.net/bazboz/"),
         ("LN", ["pat", "foo", "bar"], "http://example.com/foo/bar/"),
         ("LN", "beer", "http://example.com/beer"),
         ("NS", "neighbor", "http://example.net/"),
         ("PATTERN", "pat", "http://example.com/$ARG1/$ARG2/"),
         ("X", "FINAL", ["http://example.com/$NAME"]),
         ("X", "VERSION", ["1.2"]),]
    
    def setUp(self):
        """DOC"""
        TestThatUsesTestStore.setUp(self)
        self.style = lncore.Traditional(self.store)
    
    def testLookups(self):
        """Try out several lookups on the Traditional Style."""
        for (record_type, lookup, url) in TraditionalStyleTest.L:
            result = self.style.find("http://example.com/",
                                     lookup, record_type)
            assert result == (0, url)


class TestKeyHashOrderedDictionary(unittest.TestCase):
    
    """DOC
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        """DOC"""
        self.D = lncore.KeyHashOrderedDictionary()
        self.D["foo bar"] = "baz"
        self.D["baz boz"] = "foo bar"
    
    def testRetrieval(self):
        """DOC"""
        assert self.D["foobar"] == "baz"
        assert self.D["baz   boz"] == "foo bar"
    
    def testDelete(self):
        """DOC"""
        del self.D["foo bars"]
        assert self.D.get("foo bar") == None
    
    def testLoad(self):
        """Testing loading data from another ordered dictionary."""
        ordered = lncore.OrderedDictionary()
        ordered["foo bar"] = "baz"
        ordered["baz boz"] = "foo bar"
        keyhash = lncore.KeyHashOrderedDictionary()
        keyhash.load_from(ordered)
        assert keyhash.order() == ["foobar", "bazboz"]
        assert keyhash["foobar"] == "baz"
        assert keyhash["baz   boz"] == "foo bar"


if __name__ == "__main__":
    unittest.main() # run all tests

