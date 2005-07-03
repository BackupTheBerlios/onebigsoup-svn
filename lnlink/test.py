"""Test lnlink.

TODO - write out table of classes
"""

import unittest

import lnlink


class DictionarySetupTestBase(unittest.TestCase):

    """Inherit from this to get a basic dictionary."""

    def setUp(self):
        """Setup with a basic names-urls dictionary."""
        self.dictionary = {"slashdot": "http://www.slashdot.org/",
                           "freshmeat": "http://www.freshmeat.net/",
                           "kuroshin": "http://www.kuro5hin.org/",
                           "google": "http://www.google.com/"}


class StringMatchingTests(DictionarySetupTestBase):

    """Test lnlink HTML linking.
    
    test1  -- general input/output test
    """

    def test1(self):
        """General input/output test.

        Given a bunch of input text, make sure that it produces
        the corresponding output text.
        """
        input_text = '\n<html>\n  <p><a href="slashdot">/.</a></p>\n</html>\n'
        correct_output = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n  <p><a href="http://www.slashdot.org/">/.</a></p>\n</html>'
        actual_output = lnlink.link_names(input_text, self.dictionary)
        assert correct_output == actual_output, "General test #1 fails."


class HTMLFragmentTests(DictionarySetupTestBase):

    """Test lnlink HTML fragment linking.

    test1  -- general input/output test
    """
    
    def test1(self):
        """General input/output test.

        Given a bunch of input text, make sure that it produces
        the corresponding output text.
        """
        input_text = '''<p><a href="slashdot">/.</a></p>'''
        correct_output = '<p><a href="http://www.slashdot.org/">/.</a></p>'
        actual_output = lnlink.link_names_in_fragment(input_text,
                                                      self.dictionary)
        assert correct_output == actual_output, "General test #1 fails."


class RemoteLookupTest(unittest.TestCase):

    """Test that we can remotely look up names.

    test1  -- test some lookups, using Lion's namespace description.
    """

    def test1(self):
        """Make sure bind_with_LNQS is resolving everything.

        If there's an error, it may be that it actually can't resolve
        slashdot or freshmeat- you'll have to check it independently,
        should this fail.
        """
        collection = lnlink.CollectedNames(["slashdot", "freshmeat"])
        result = collection.bind_with_LNQS(
            "http://taoriver.net/tmp/gmail.txt",
            "http://services.taoriver.net:9090/")
        assert len(result) == 0, "still some unresolved names"
        bound = collection.bound
        assert bound["slashdot"] == "http://www.slashdot.org/"
        assert bound["freshmeat"] == "http://www.freshmeat.net/"


if __name__ == '__main__':
    unittest.main()

