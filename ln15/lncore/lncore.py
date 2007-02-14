"""Local Names Core

DOC

TODO: Cache a namespace description.
TODO: setup.py
TODO: Interpret a namespace description.
TODO: Resolve names by style.

DOC
"""


import webcache


## The Imaginaries
##
## Imaginaries are constructs in RAM for the temporary storage of data.


class NameSpace:
    
    """A space containing names; the RAM memory of a namespace.
    
    DOC
    
    Every web page has a "bboard," a dictionary that stores data for
    that independent styles will reference, and attach to the page.

    In Local Names 1.4, ".final(args)" returned the result of applying
    the args to the X "FINAL" pattern (if it was a pattern.)  This work
    differently in Local Names 1.5:  1. If rel="default_localname" is defined, proceed.  2. If it is a pattern,  fit it, and then return the result.  3. If it is not a pattern, it's a namespace hop: Pop an argument, and then continue, from the namespace.
    
    DOC
    """
    
    def __init__(self):
        """DOC"""
        self.title = None
        self.default_localname = None
        self.defaulting_namespaces = []
        self.names = {}  # "name" -> "URL"
        self.bboard = {}  # "style name" -> (style object)
    
    def get_bboard(self, name):
        """Get a blackboard of a given name.
        
        A blackboard is an attached dictionary other objects can store
        data in. Every blackboard has a name.
        """
        return self.bboard.setdefault(name, {})

