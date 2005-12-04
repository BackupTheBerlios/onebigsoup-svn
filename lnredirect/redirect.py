#!/usr/bin/env python2.3
"""Local Names web browser redirection services.

The server redirects the client web browser to a web page.

1. The web browser client sends a query in the request URI.
2. The query is transformed into a namespace URL and a lookup path.
3. The namespace URL and lookup path are resolved to an URL.
3. The browser is then redirected to the URL that was found.

Example URL

  http://example.net/redirect.cgi?namespace=http://example.com/ns.txt
                                 &path=foo:bar:baz

Install the script by placing the CGI in a directory.

You need the URL of an Local Names XML-RPC Query Interface.
"""

import cgi
import xmlrpclib

import cgitb; cgitb.enable()


LNXRQUERYI = "http://localhost:8080/"


BAD_QUERY_RESPONSE="""Content-type: text/plain

You need to specify both namespace & path.

ex:

    http://example.net/redirect.cgi?namespace=http://example.com/ns.txt
                                   &path=foo:bar:baz
"""


if __name__ == "__main__":
    form = cgi.FieldStorage()
    ns_url = form.getvalue("namespace", None)
    path = form.getvalue("path", None)
    server = xmlrpclib.ServerProxy(LNXRQUERYI)
    if (ns_url is None) or (path is None):
        print BAD_QUERY_RESPONSE
    else:
        result = server.lnquery.find(ns_url, path, "LN", "traditional")
        if result[0] != "0":
            print "Content-type: text/plain"
            print
            print "There was a problem while looking up the name:"
            print "error code:", result[0]
            print "error string:", result[1]
        else:
            print "Location:", result[1]
            print

