"""DOC

DOC

DOC
"""

import unittest

import lncore


basic_text = """
X "VERSION" "1.2"
LN "foo" "http://example.com/"
LN "bar" "http://example.com/"
X "FINAL" "http://example.com/$NAME"
"""

'''Basic namespace description for use in simple tests.'''


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
               (lncore.Line.BLK,
                None, None, None),]
    
    def testLines(self):
        """DOC"""
        lines = lncore.tokenize(basic_text)
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
        lines = lncore.tokenize(basic_text)
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


if __name__ == "__main__":
    unittest.main() # run all tests

