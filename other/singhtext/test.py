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
    
    test1  -- general input/output test
    """

    def test1(self):
        """General input/output test.

        Given a bunch of input text, make sure that it produces
        the corresponding output text.
        """
        input_text = '\n= Example =\n\n$name Basics\n== Basics ==\n\nThis is a paragraph made of multiple lines of text.  We\'re doing this so\nthat we can later parse it together into something we\'ll call a\n"paragraph," which can contain \'\'\'bold\'\'\' and \'\'italic\'\' text, as well\nas other stuff. Here\'s a [[Local Name]] for you, as well as a\ntraditional [[http://example.net/] link.]\n\nLearn about Local Names: [[http://ln.taoriver.net/]]\n\nHere\'s another paragraph. It\'s made of multiple lines. It has features\nsome tricky "entities" like <this> for HTML to deal with.\n\n# item 1\n# item 2\n** item 2-A\n** item 2-B\n** item 2-C\n# item 3\n# A paragraph of text.\nThis is made by just placing line after line after line\nof text after the list item.\n\n$name Regions\n== Regions ==\n\nCode:\n\n#CODE\n<foo>\n  <bar/>\n  <baz/>\n</foo>\n#CODE\n\nLiteral:\n\n#LITERAL\n<table border=\'1\'>\n<tr>\n<td>row 1 column 1</td>\n<td>row 1 column 2</td>\n</tr>\n<tr>\n<td>row 2 column 1</td>\n<td>row 2 column 2</td>\n</tr>\n</table>\n#LITERAL\n\n'
        correct_output = '<h1> Example </h1>\n<a name=\'Basics\'/>\n<h2> Basics </h2>\n<p>This is a paragraph made of multiple lines of text.  We&apos;re doing this so\nthat we can later parse it together into something we&apos;ll call a\n&quot;paragraph,&quot; which can contain <b>bold</b> and <i>italic</i> text, as well\nas other stuff. Here&apos;s a <a href="Local Name">Local Name</a> for you, as well as a\ntraditional <a href="http://example.net/"> link.</a>\n</p>\n<p>Learn about Local Names: <a href="http://ln.taoriver.net/">http://ln.taoriver.net/</a>\n</p>\n<p>Here&apos;s another paragraph. It&apos;s made of multiple lines. It has features\nsome tricky &quot;entities&quot; like &lt;this&gt; for HTML to deal with.\n</p>\n<ol>\n<li>item 1</li>\n<li>item 2</li>\n<ul>\n<li>item 2-A</li>\n<li>item 2-B</li>\n<li>item 2-C</li>\n</ul>\n<li>item 3</li>\n<li>A paragraph of text. This is made by just placing line after line after line\n of text after the list item.\n</li>\n</ol>\n<a name=\'Regions\'/>\n<h2> Regions </h2>\n<p>Code:\n</p>\n<p><code><pre>&lt;foo&gt;\n  &lt;bar/&gt;\n  &lt;baz/&gt;\n&lt;/foo&gt;\n</pre></code></p>\n<p>Literal:\n</p>\n<table border=\'1\'>\n<tr>\n<td>row 1 column 1</td>\n<td>row 1 column 2</td>\n</tr>\n<tr>\n<td>row 2 column 1</td>\n<td>row 2 column 2</td>\n</tr>\n</table>\n'
        actual_output = singhtext.text_to_html(input_text)
        assert correct_output == actual_output, "General test #1 fails."


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
        correct_output = "<p>This is a test.\n</p>\n<a name='foo'/>\n<p>This paragraph should be named, &quot;foo.&quot;\n</p>\n<a name='bar'/>\n<p>And this paragraph should be named, &quot;bar.&quot;\n</p>"
        actual_output = singhtext.text_to_html(self.input_text)
        assert actual_output == correct_output, "Names to HTML failure."


if __name__ == '__main__':
    unittest.main()

