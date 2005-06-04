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


if __name__ == '__main__':
    unittest.main()

