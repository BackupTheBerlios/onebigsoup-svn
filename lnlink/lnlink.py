"""Link Local Names to URLs.

Read an XHTML document and bind Local Names found in <a href> and <img>
tags to URLs.

Any <img src="..."> attribute or any <a href="..."> attribute that ends
with .gif, .jpg, .png, .html, or / is assumed to be a URL or relatively
addressed page or image. Everything else is assumed to be a Local Name.

The recognized page and image extensions are customizable.

If a name is not resolved, it is left as it is. (That is, no changes are
made.) You may want to bind all unresolved names to some error URL.

In the common case, Local Names are resolved via remote name server.
Thus, this is generally a two step process: First pass, you collect
names to resolve from the XHTML. Then you resolve the names to URLs.
Then you make your second pass, and output the URLs in place of the
names.

You want to collect the names first, because the network call to resolve
them is expensive. You want to make one network call, rather than one
per name you're resolving.

NamesCollector  -- SAX Handler that collects Local Names
TagManipulator  -- SAX filter that tweaks attributes
find_names  -- Find names in XHTML
link_names  -- Link names in XHTML
"""

import cStringIO as StringIO
import sets
import xml.sax
import xml.sax.xmlreader
import xml.sax.handler
import xml.sax.saxutils


ignore_extensions = [".gif", ".jpg", ".png", "/", ".html"]


def ignore_url(url):
    """Return true if this is not interpreted as a Local Name."""
    for x in ignore_extensions:
        if url.endswith(x):
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

    """Build a list of names to lookup, given XHTML."""

    result = sets.Set()
    
    parser = xml.sax.make_parser()
    parser.setContentHandler(NamesCollector(result))

    inpsrc = xml.sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO.StringIO(xhtml))

    parser.parse(inpsrc)

    return result


def link_names(xhtml, dictionary):
    
    """Link Local Names found in XHTML."""

    output = StringIO.StringIO()
    
    parser = xml.sax.make_parser()
    
    _filter = TagManipulator(dictionary, parser)
    parser.setContentHandler(_filter)
    _filter.setContentHandler(xml.sax.saxutils.XMLGenerator(output))
    
    inpsrc = xml.sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO.StringIO(xhtml))
    
    parser.parse(inpsrc)

    return output.getvalue()


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

