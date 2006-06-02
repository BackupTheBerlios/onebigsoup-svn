"""Link local names to URLs.

Read an XHTML document and bind local names found in <a href> and <img>
tags to URLs.

Given an <a href="...">, is it a local name?
* assume it's a local name
* unless it ends with: .gif, .jpg, .png, .html, or /
* unless it starts with: http://, ftp://

Customize prefixes and suffixes with .ignore_suffixes, .ignore_prefixes.

Unresolved names can be bound to a URL, or left be (no changes made.)

Resolving names is a two pass process:
* first pass, collect local names to resolve from XHTML
* (resolve names)
* second pass, replace local names with URLs

The process is two pass, because network calls to resolve local names
are expensive: We need to be able to resolve all names in one trip.

Local names can be manually bound, or resolved automatically with the
Old Style Local Names Query Server.

.ignore_suffixes  -- URL extensions that are not Local Names
.ignore_prefixes  -- URL prefixes that are not Local Names
ignore_url  -- is string ignored (URL? file?) or not (Local Name)
NamesCollector  -- SAX Handler that collects Local Names
TagManipulator  -- SAX filter that tweaks attributes
CollectedNames  -- collection of names to be bound
collect_names  -- Find names in XHTML
link_names  -- Link names in XHTML
collect_names_in_fragment  -- Find names in XHTML fragment
link_names_in_fragment  -- Link names in XHTML fragment
"""

import cStringIO as StringIO
import sets
import xml.sax
import xml.sax.xmlreader
import xml.sax.handler
import xml.sax.saxutils


ignore_suffixes = [".gif", ".jpg", ".png", "/", ".html", ".txt"]
ignore_prefixes = ["http://", "ftp://", "irc://"]

LIONS_OSLNQS_URL = "http://services.taoriver.net:9090/"


def ignore_url(url):
    """Return true if this is not interpreted as a Local Name."""
    for x in ignore_suffixes:
        if url.endswith(x):
            return True
    for x in ignore_prefixes:
        if url.startswith(x):
            return True
    return False


class NamesCollector(xml.sax.handler.ContentHandler):
    
    """Collect Local Names to resolve from an XML stream."""
    
    def __init__(self, names_collected=sets.Set()):
        """Build a names collector.

        If you don't pass a set of names_collected yourself, you can
        access the .names set yourself, to get the names.
        """
        self.collection = names_collected
    
    def startElement(self, name, attrs):
        if name == "a":
            if attrs.has_key("href") and not ignore_url(attrs["href"]):
                self.collection.add(attrs["href"])
        elif name == "img":
            if attrs.has_key("src") and not ignore_url(attrs["src"]):
                self.collection.add(attrs["src"])


class TagManipulator(xml.sax.saxutils.XMLFilterBase):

    """Manipulate <img src="..."> and <a href="..."> tags in XHTML.

    A SAX XMLReader reads XHTML, and passes the information to a SAX
    Handler. In our case, the Handler is just an XMLGenerator- resulting
    in a copy of the original XHTML.

    This TagManipulator, however, is placed between the XMLReader and
    the XMLGenerator. It looks for <a> and <img> tags, checks the
    attributes, and performs Local Names substitutions where it can.
    """

    def __init__(self, definitions, parent=None):
        """Initialize a TagManipulator with Local Names definitions.

        definitions is a dictionary-like object that defines the values
        of Local Names.
        """
        self.definitions = definitions
        xml.sax.saxutils.XMLFilterBase.__init__(self, parent)

    def startElement(self, name, attrs):

        """Intercept the beginning of an <img src> or <a href>."""

        def pass_on():
            xml.sax.saxutils.XMLFilterBase.startElement(self, name,
                                                        attrs)

        def mask(key):
            attrs2 = attrs.copy()
            new_val = self.definitions.get(attrs2[key], attrs2[key])
            attrs2._attrs[key] = new_val  # Hack
            xml.sax.saxutils.XMLFilterBase.startElement(self, name,
                                                        attrs2)
        
        if name == "img":
            if not attrs.has_key("src") or ignore_url(attrs["src"]):
                pass_on()
                return
            mask("src")
            return
        
        if name == "a":
            if not attrs.has_key("href") or ignore_url(attrs["href"]):
                pass_on()
                return
            mask("href")
            return
        
        pass_on()


class CollectedNames:

    """A collection of local names, to be bound to URLs.

    This class represents a collection of local names that are bound, or
    to be bound, to URLs.

    add  -- add name to collect
    update  -- add several names to collect
    bind  -- bind names to values
    bind_unresolved_to_url  -- bind all unresolved names to an URL
    bind_with_LNQS  -- use LNQS to bind names
    .unresolved  -- set of unresolved names
    .bound  -- dictionary of bindings
    """

    def __init__(self, unresolved=set(), bound={}):
        """Initialize, optionally with names bound or otherwise."""
        if isinstance(unresolved, list):
            unresolved = set(unresolved)
        self.unresolved = unresolved
        self.bound = bound

    def add(self, localname):
        """Add a name to be collected.

        If the name is already defined, it is not added.
        """
        if localname not in self.bound:
            self.unresolved.add(localname)

    def update(self, localnames):
        """Add several names to be collected.

        If a name is already defined, it is not added.
        """
        for localname in localnames:
            if localname not in self.bound:
                self.unresolved.add(localname)
    
    def bind(self, bindings, overwrite=False):
        """Safely bind local names to values.

        Return the set of bindings that were rejected, because they were
        already defined. (If overwrite is true, returns an empty list.)

        It's okay to bind something that hasn't been requested yet.
        """
        rejected = set()
        for key in bindings:
            if overwrite or key not in self.bound:
                self.bound[key] = bindings[key]
                self.unresolved.discard(key)
            else:
                rejected.add(key)
        return rejected

    def bind_unresolved_to_url(self, url):
        """Bind all unresolved names to a given URL."""
        for localname in self.unresolved:
            self.bound[localname] = url
        self.unresolved = set()
    
    def bind_with_LNQS(self, namespace_description_url, xmlrpc_url,
                       separator=":"):
        """Bind unresolved local names with a Local Names Query Server.
	
        Returns set of names that were not resolved.
	
        xmlrpc_url is the URL of an Local Names XML-RPC Query Interface.
        """
        import xmlrpclib
        ns = xmlrpclib.ServerProxy(xmlrpc_url)
        request_names = list(self.unresolved)
        request_paths = []
        for name in request_names:
            request_paths.append(name.split(separator))
        responses = ns.lnquery.find_many(namespace_description_url,
                                         request_paths, "LN", "default")
        for (key, value) in zip(request_names, responses):
            if value[0] == 0:
                self.bound[key] = value[1]
                self.unresolved.discard(key)
        return self.unresolved
    
    def bind_with_OSLNQS(self, namespace_description_url,
                         xmlrpc_url=LIONS_OSLNQS_URL, separator=":"):
        """Bind unresolved local names using an OSLNQS. (deprecated)
        
        Returns set of names that were not resolved.
        
        An "OSLNQS" is an "Old Style Local Names Query Server." Or
        perhaps "Old School Local Names Query Server." Regardless, this
        is an old query server, pre-Local Names XML-RPC Query Interface
        (LNXRQI) specification.
        
        Since it seems only one name server on the web meets the
        description, and since this is only in use until the interface
        specification is completed an a formal LNSQ, and thus this
        function is almost automatically obsolete, I feel no guilt in
        hard-coding it to Lion's OSLNQS.
        
        The Local Names XML-RPC Query Interface (LNXRQI) specification
        is scheduled for completion October 2005, and a working Local
        Names Query Server (LNQS) scheduled for completion November
        2005.
        
        This function will be depricated, and perhaps useless, as soon
        as we have an alternative LNQS.
        """
        import xmlrpclib
        flags = ["loose", "check-neighboring-spaces"]
        nameserver = xmlrpclib.ServerProxy(xmlrpc_url)
        request_names = list(self.unresolved)
        request_paths = []
        for name in request_names:
            request_paths.append(name.split(separator))
        urls = nameserver.lookup(request_paths,
                                 namespace_description_url, flags)
        for (key, value) in zip(request_names, urls):
            if isinstance(value, basestring):
                self.bound[key] = value
                self.unresolved.discard(key)
        return self.unresolved


def collect_names(xhtml, collected_names=CollectedNames()):

    """Build a set of names to lookup, given XHTML.

    The XHTML must be a complete XHTML document, with no errors.

    Returns a CollectedNames instance; Read the .unresolved attribute
    for the set of names to look up.
    """
    
    parser = xml.sax.make_parser()
    parser.setContentHandler(NamesCollector(collected_names.unresolved))
    
    inpsrc = xml.sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO.StringIO(str(xhtml)))
    
    parser.parse(inpsrc)
    
    return collected_names


def link_names(xhtml, collected_names):
    
    """Link Local Names found in XHTML.
    
    collected_names can be a dictionary or a CollectedNames instance.
    
    The XHTML must be a complete XHTML document, with no errors.
    """

    if isinstance(collected_names, CollectedNames):
        collected_names = collected_names.bound
    
    output = StringIO.StringIO()
    
    parser = xml.sax.make_parser()
    
    _filter = TagManipulator(collected_names, parser)
    parser.setContentHandler(_filter)
    _filter.setContentHandler(xml.sax.saxutils.XMLGenerator(output))
    
    inpsrc = xml.sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO.StringIO(str(xhtml)))
    
    parser.parse(inpsrc)

    return output.getvalue()


def collect_names_in_fragment(xhtml_fragment):
    """Build a set of names to lookup, given an XHTML fragment.
    
    The fragment must contain no errors.

    Returns a CollectedNames instance; Read the .unresolved attribute
    for the set of names to look up.

    This is a convenience function.
    """
    return collect_names('<html>' + xhtml_fragment + '</html>')


def link_names_in_fragment(xhtml_fragment, collected_names):
    """Link Local Names found in XHTML fragment.

    collected_names can be a dictionary or a CollectedNames instance.
    
    The fragment must contain no errors.

    This is a convenience function.

    It's also something of a hack. If anyone knows the proper solution,
    I'd love to know it. Mail lion at speakeasy.org. 2006-06-03.
    """
    test_string = "<p></p>"
    test_result = link_names(test_string, {})
    xml_header_len = test_result.find(test_string)
    
    full = link_names('<html>' + xhtml_fragment + '</html>',
                      collected_names)
    return full[xml_header_len:][len('<html>'):-len('</html>')]


def _visual_test():
    test_xml = """
    <xhtml>
    <h2>Hello, World!</h2>
    <p>This is <a href="http://example.net/normal/">a test.</a></p>
    <p>Here is another.</p>
    <img src="Local Names Diagram"/>
    <p>Next, a <a href='Local Names'>Local Name!</a></p>
    <p>All done!</p>
    </xhtml>
    """
    print collect_names(test_xml)
    names = {"Local Names": "http://ln.taoriver.net/"}
    print link_names(test_xml, names)


if __name__ == "__main__":
    _visual_test()

