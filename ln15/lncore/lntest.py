"""DOC

DOC

DOC
"""

import unittest

import lncore


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


class TestBasicMicroformatParsing(unittest.TestCase):

    """DOC

    DOC

    DOC
    """

    def setUp(self):
        
