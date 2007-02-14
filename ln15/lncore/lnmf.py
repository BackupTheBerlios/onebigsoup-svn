"""Local Names MicroFormat Parser

This is a temporary file.

It'll go away after it's merged into lncore.
"""

import elementtree.ElementTree


class NamespaceDictionary(dict):
    
    """Dictionary customized for Namespace storage."""
    
    blank = {"X": {"STRICT": None,
                   "TITLE": None},
             "?": {},
             "LN": {},
             "NS": {},
             "PATTERN": {}}
    
    def __init__(self):
        dict.__init__(self)
        self.update(NamespaceDictionary.blank)
    
    def pprint(self):  # XXXLEO_DEL
        import pprint
        pprint.pprint(self)
    
    def join(self):
        """Add ? bindings to LN bindings.
        
        However, ? bindings should not over override LN bindings.
        
        This function always destroys the ? bindings.
        """
        self["?"].update(self["LN"])
        self["LN"] = self["?"]
        del self["?"]
    
    def switch(self):
        """Add ? bindings to LN bindings if there are no LN bindings.
        
        If there's a single LN binding, don't make use of ? bindings.
        If there are none, make the ? bindings the LN bindings.
        
        This function always destroys the ? bindings.
        """
        if len(self["LN"]) == 0:  # no ln-localnames?
            self["LN"] = self["?"]  # assume ln-localname
        del self["?"]


class MicroformatsParser:
    
    """Read Local Names namespace description from an XHTML page.
    
    DOC
    
    DOC
    """
    
    def __init__(self, switching=False):
        """Initialize a Microformats Parser
        
        What is "switching" about?
        
        I haven't made a decision yet on whether Local Names should use
        "switching," or "not switching" behavior yet.
        
        That is, given a namespace description, being interpreted lazy,
        and you come cross an unmarked hyperlink, what do you do?  Do
        you toss it, or do you consider it a local name?  In
        "switching," whether you do that or not is switched based on
        whether there are any rel=ln-localname's present.  If there are,
        you ignore anything that's not.  But if there aren't, you keep
        them all.
        
        For now, this is user choice.  But I'm leaning towards
        "non-switching," because it's easier to understand.
        """
        self.switching = switching
    
    def _assemble_subtext(self, e):
        """Collect all text, recursively, beneath this node.
        
        This exists, because there are links such s:
        <a href="..."><b>name</b></a>
        """
        children = e.getchildren()
        if children is None:
            child_text = ""
        else:
            child_text = "".join([self._assemble_subtext(x)
                                  for x in children])
        return (e.text or "") + child_text
    
    def _recursive_read(self, D, e):
        """Read Local Names items from the element's children."""
        if e.tag == "title":
            D["X"]["TITLE"] = e.text
        if e.tag == "a":
            name = self._assemble_subtext(e)
            rels = e.get("rel", "").split()
            href = e.get("href")
            if name and (href is not None):
                if "ln-ignore" in rels:
                    pass
                elif "ln-localname" in rels:
                    D["LN"][name] = href
                elif "ln-namespace" in rels:
                    D["NS"][name] = href
                elif "ln-pattern" in rels:
                    D["PATTERN"][name] = href
                else:
                    D["?"][name] = href
        for e2 in e:
            self._recursive_read(D, e2)
        return D
    
    def parse(self, xhtmltext, force_strict=False):
        """DOC
        
        Errors raised:
        * xml.parsers.expat.ExpatParser
        
        try:
            parser.parse(xhtmltext)
        except xml.parsers.expat.ExpatError:
            # There was an error parsing the XML.
            pass
        """
        print "--------------------"
        root = elementtree.ElementTree.fromstring(xhtmltext)
        D = NamespaceDictionary()
        D["X"]["STRICT"] = False  # default NOT strict
        D = self._recursive_read(D, root)
        if force_strict or D["X"]["STRICT"]:
            del D["?"]  # assume ln-ignore
        else:
            if self.switching:
                D.switch()
            else:
                D.join()
        return D

