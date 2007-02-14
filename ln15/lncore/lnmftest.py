"""DOC

DOC

Bugs SPLAT by virtue of automated testing:
#1: blank hrefs
  "if name and href:" -> "if name and (href is not None):"
  I wasn't getting blank href's! (self reference)

DOC
"""

import unittest

import lnmf


def testdata(house="myhouse", page="namespace.html"):
    """DOC"""
    return open("../testdata/local/%s/%s" % (house, page)).read()

my_namespace_xhtml = testdata("myhouse", "namespace.html")
my_bad_xml_xhtml = testdata("myhouse", "bad_xml.html")
my_no_ln_localname_xhtml = testdata("myhouse", "no_ln_localname.html")

# Matching Dictionaries
#
# "S" means "Switched"
# "J" means "Joined"
# "MD" just means: "Match Dictionary"

MD_my_namespace_S = {"LN": {"chair": "chair.html",
                            "table": "table.html",
                            "Johns House": "../johnshouse/homepage.html",
                            "Janes House": "../janeshouse/homepage.html"},
                     "NS": {"this": "",
                            "this2": "namespace.html",
                            "Johns House": "../johnshouse/namespace.html",
                            "Janes House": "../janeshouse/namespace.html"},
                     "PATTERN": {"Computer": "computer/{number}.html"},
                     "X": {"STRICT": False,
                           "TITLE": "Local Test Namespace Description: My Namespace"}}

MD_my_namespace_J = {"LN": dict(MD_my_namespace_S["LN"]),
                     "NS": dict(MD_my_namespace_S["NS"]),
                     "PATTERN": dict(MD_my_namespace_S["PATTERN"]),
                     "X": dict(MD_my_namespace_S["X"])}
MD_my_namespace_J["LN"].update({"shrub": "shrub.html",
                                "bush": "bush.html",
                                "weed": "weed.html"})

def comparison_by_parts(TD, MD):
    """Test if the dictionaries are equal, in managable parts."""
    for k in ["LN", "NS", "PATTERN", "X"]:
        assert TD[k] == MD[k], ("mistmatch", k,
                                "test dictionary", TD[k],
                                "match dictionary", MD[k])


class TestMicroformatsParser(unittest.TestCase):
    
    """DOC
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        self.nd = lnmf.NamespaceDictionary()
    
    def tearDown(self):
        pass
    
    def variantBasicNamespaceTest(self, switching, strict, MD):
        """testBasicNamespace varies switching, and strict."""
        parser = lnmf.MicroformatsParser(switching)
        D = parser.parse(my_namespace_xhtml, strict)
        comparison_by_parts(D, MD)
    
    def testBasicNamespaceSwitchingStrict(self):
        """DOC"""
        self.variantBasicNamespaceTest(True, True, MD_my_namespace_S)
    
    def testBasicNamespaceSwitchingLoose(self):
        """The basic namespace, switching, but not strict.
        
        The basic namespace has things that are rel="ln-localname", and
        has things that are not.  We have switching mode on, which means
        that we should ignore everything that doesn't have
        rel="ln-localname", even though we're not being strict.
        
        There should be a chair and a table, but no bush, shrub, or
        weed.
        """
        self.variantBasicNamespaceTest(True, False, MD_my_namespace_S)
    
    def testBasicNamespaceJoinedStrict(self):
        """The basic namespace, joining, but strict?
        
        What does this even mean?  How can you Join, when you're tossing
        out anything that doesn't have ln-ignore?
        
        Properly, "strict" makes joining versus switching a moot point.
        Joining can only make sense in a non-strict environment.
        
        * Strict,  -- ln-localname mandatory
        * Not Strict & Joining,  -- ln-localname optional
        * Not Strict & Switching.  -- ln-localname req'd if present on 1
        """
        self.variantBasicNamespaceTest(False, True, MD_my_namespace_S)
    
    def testBasicNamespaceJoinedLoose(self):
        """DOC"""
        self.variantBasicNamespaceTest(False, False, MD_my_namespace_J)


if __name__ == "__main__":
    unittest.main()  # run all tests

