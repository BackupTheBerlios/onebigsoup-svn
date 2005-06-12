"""Test singhtext.

TODO:
* write a test for italic, bold, linking, &entities; within things like
  lists, header, etc., etc.,.

TODO - write out table of classes
"""

import unittest
import pprint  # Delete this one

import singhtext


class StringMatchingTests(unittest.TestCase):

    """Test SinghText HTML generation.
    
    testMultilineLinks  - links that span multiple lines
    testSpecialLineInterference  - $special intefere with headers?
    """

    def testMultilineLinks(self):
        """Test links that span multiple lines, another way."""
        input_text = '[[foo]\n bar] [[baz]]'
        output = singhtext.text_to_html(input_text)
        assert ("[[" in output) == False, "Multi-line links fail."

    def testSpecialLineInterference(self):
        """Make sure special lines don't interfere with headers."""
        input_text = '\n$foo\n== bar ==\nbaz\n'
        correct_output = '<h2> bar </h2>\n<p>baz</p>'
        actual_output = singhtext.text_to_html(input_text)
        assert "bar" in actual_output and \
               "h2" in actual_output, "$-line interference."

    def testRegionTokenizing(self):
        """Make sure regions are tokenized into one."""
        input_text = '#REGION\nfoo\nbar\n#REGION\n'
        tokens = singhtext.tokenize_all(input_text)
        assert len(tokens) == 1, "#REGION should be just 1 token."""

    def testLiteralRegions(self):
        """Make sure #LITERAL regions work."""
        input_text = '#LITERAL\n<robot>\n</robot>\n#LITERAL\n'
        actual_output = singhtext.text_to_html(input_text)
        correct_output = '<robot>\n</robot>\n'
        assert actual_output == correct_output, "Bad #LITERALs."


class SetTests(unittest.TestCase):

    """Test $set.

    testDictionary  -- collect values from $set lines, check them
    """

    def testDictionary(self):
        """General $set dictionary test.

        Make sure that a dictionary is produced by several properly
        formated $set lines.
        """
        input_text = '\n$set foo: 14\n$set bar: 42\n$set baz: xyzzy\n'
        set_dict = singhtext.text_to_variables(input_text)
        assert set_dict["foo"] == "14", "Set dict binding failure (1)."
        assert set_dict["bar"] == "42", "Set dict binding failure (2)."
        assert set_dict["baz"] == "xyzzy", \
               "Set dict binding failure (3)."


class NamesTests(unittest.TestCase):

    """Test $title.

    testNamesList  -- check list returned
    testNamesHTML  -- check HTML returned
    """

    def setUp(self):
        """Setup base text for tests."""
        self.input_text = 'This is a test.\n\n$name foo\nThis paragraph should be named, "foo."\n\n$name bar\nAnd this paragraph should be named, "bar."\n'

    def testNamesList(self):
        """Check list produced by $name lines."""
        L = singhtext.text_to_names_list(self.input_text)
        assert L == ["foo", "bar"], "Names list production failure."

    def testNamesHTML(self):
        """Check HTML produced by $name lines."""
        correct_output = "<p>This is a test.</p>\n<a name='foo'/>\n<p>This paragraph should be named, &quot;foo.&quot;</p>\n<a name='bar'/>\n<p>And this paragraph should be named, &quot;bar.&quot;</p>"
        actual_output = singhtext.text_to_html(self.input_text)
        assert actual_output == correct_output, "Names to HTML failure."


if __name__ == '__main__':
    unittest.main()

