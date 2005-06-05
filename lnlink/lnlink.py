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

NamesCollector  -- SAX Handler that collects Local Names
TagManipulator  -- SAX filter that tweaks attributes
collect_names  -- Find names in XHTML
link_names  -- Link names in XHTML
collect_names_in_fragment  -- Find names in XHTML fragment
link_names_in_fragment  -- Link names in XHTML fragment
ignore_url  -- is string ignored (URL? file?) or not (Local Name)
.ignore_suffixes  -- URL extensions that are not Local Names
.ignore_prefixes  -- URL prefixes that are not Local Names
"""

import cStringIO as StringIO
import sets
import xml.sax
import xml.sax.xmlreader
import xml.sax.handler
import xml.sax.saxutils


ignore_suffixes = [".gif", ".jpg", ".png", "/", ".html", ".txt"]
ignore_prefixes = ["http://", "ftp://"]


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
        self.names = names_collected
    
    def startElement(self, name, attrs):
        if name == "a":
            if attrs.has_key("href") and not ignore_url(attrs["href"]):
                self.names.add(attrs["href"])
        elif name == "img":
            if attrs.has_key("src") and not ignore_url(attrs["src"]):
                self.names.add(attrs["src"])


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


def collect_names(xhtml):

    """Build a list of names to lookup, given XHTML.

    The XHTML must be a complete XHTML document, with no errors.
    """
    
    result = sets.Set()
    
    parser = xml.sax.make_parser()
    parser.setContentHandler(NamesCollector(result))
    
    inpsrc = xml.sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO.StringIO(xhtml))
    
    parser.parse(inpsrc)
    
    return result


def link_names(xhtml, dictionary):
    
    """Link Local Names found in XHTML.

    The XHTML must be a complete XHTML document, with no errors.
    """
    
    output = StringIO.StringIO()
    
    parser = xml.sax.make_parser()
    
    _filter = TagManipulator(dictionary, parser)
    parser.setContentHandler(_filter)
    _filter.setContentHandler(xml.sax.saxutils.XMLGenerator(output))
    
    inpsrc = xml.sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO.StringIO(xhtml))
    
    parser.parse(inpsrc)

    return output.getvalue()


def collect_names_in_fragment(xhtml_fragment):
    """Build a list of names to lookup, given an XHTML fragment.
    
    This is a convenience function.

    The fragment must contain no errors.
    """
    return collect_names('<html>' + xhtml_fragment + '</html>')


def link_names_in_fragment(xhtml_fragment, dictionary):
    """Link Local Names found in XHTML fragment.
    
    This is a convenience function.

    The fragment must contain no errors.

    It's also something of a hack. If anyone knows the proper solution,
    I'd love to know it. Mail lion at speakeasy.org. 2006-06-03.
    """
    test_string = "<p></p>"
    test_result = link_names(test_string, {})
    xml_header_len = test_result.find(test_string)
    
    full = link_names('<html>' + xhtml_fragment + '</html>', dictionary)
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

