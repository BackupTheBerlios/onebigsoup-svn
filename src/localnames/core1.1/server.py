#!/usr/bin/python2.3
"""
Python2.3 Local Names 1.1 server

"""

import BaseHTTPServer
import cgi
import xmlrpclib
import xml.parsers.expat
import sets
import time

import localnames


redir_lookup_flags = sets.ImmutableSet(["loose", "check-neighboring-spaces"])

xmlrpc_documentation = '''
<html>
<head><title>Local Names Server 1.1 XML-RPC interface</title></head>
<body>
  Not yet!
</body>
'''

filterData_p = '''Replaces marked up text with HTML links.

filterData is an implementation of Les Orchard\'s
XmlRpcFilteringPipe. It can be called as either
"filterData", or in the traditional "wiki" namespace
("wiki.filterData".)

Argument 1: The text to perform replacements on.

Argument 2: "text/plain; charset=utf-8" (always)

Argument 3: A structure / dictionary with one key, "namespace."
            The value for the key is the URL of the namespacen
            you want to resolve Local Names from.

The markup is like so:

  [[name]]  : look up a name, and link it.
              <a href="http://foobar/">name</a>

  [[name]frozboz]  : look up a name, and link it with
                     alternative text.
                     <a href="http://foobar/">frozboz</a>

  [[name][name]frozboz]   : look up a path, and link
                            it with alternative text.

  [[name][name][name][name]frozboz]  : You can go as long
                                       as you like.

  ((name))  : Soft linking- forms a link that works via
              the nameservers redirection engine, rather
              than just pointing straight at the thing
              pointed to. That is, the link will be resolved
              at click-time, dynamically via the name
              servers Location: redirection, rather than at
              text replacement time.

Local Names are resolved from the namespace description
specified in the "namespace" argument.

Example:

    filterData("[[Lion Kimbro]] works on [[Local Names.]]",
               "text/plain; charset=utf-8",
               {"namespace": "http://taoriver.net/tmp/gmail.txt"})

  Returns:
      
      ['<a href="http://www.speakeasy.org/~lion/">Lion Kimbro</a>
        works on <a href="http://ln.taoriver.net/">Local Names.</a>',
       'text/plain; charset=utf-8']
'''

filterData_h = ''
filterData_s = [('string', 'string'),
                ('string', 'string', 'struct')]
xmlrpc_info = {'filterData': {"plain": filterData_p,
                              "html": filterData_h,
                              "sig": filterData_s,}}


def un_unicode_dict(d):
    """Convert the keys in a dictionary from Unicode strings to Python strings."""
    d2 = {}
    for k,v in d.items():
        if type(k) == type(u'string'):
            if type(v) == type({}):
                v = un_unicode_dict(v)
            d2[k.encode('utf-8','replace')] = v
    return d2


class LocalNamesHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """Handles GET, POST, and interprets ULI, GTF, XML-RPC."""
    
    def do_GET(self):
        if self.path.startswith("/?"):
            args = cgi.parse_qs( self.path[2:] )
        else:
            args = {}

        if args.get("action") == ["redir"] and \
           args.get("namespace") != None and \
           (args.get("lookup") != None or args.get("path") != None):
            if args.has_key("path") and not args.has_key("lookup"):
                args["lookup"] = args["path"][0].split("/")
            url = localnames.lookup(args["lookup"],
                                    args["namespace"][0],
                                    redir_lookup_flags)
            self.send_response(301)
            self.send_header("Location", url)
            self.end_headers()
            return

        if args.get("action") == ["cached"]:
            draw = []
            html = args.get("html") != None
            for url, preferred_name, ttl in self.xmlrpc_cached():
                if html:
                    row = u'<tr><td><a href="%s">%s</a></td><td>%d</td></tr>'
                else:
                    row = u'%50s | %15s | %d'
                draw.append(row % (url.ljust(50),
                                   preferred_name.ljust(15), ttl))
            self.send_response(200)
            self.send_header("Content-type", {True:"text/html",
                                              False:"text/plain"}[html])
            self.end_headers()
            self.wfile.write(u'\n'.join(draw))
            return
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if args.get("action") == "xmlrpc":
            self.wfile.write(xmlrpc_documentation)
            return
        
        self.wfile.write('<html>'
                         '<head><title>Local Names Server 1.1</title></head>'
                         '<body><p>Local Names Server 1.1</p></body>'
                         '</html>')

    def do_POST(self):
        clen = int(self.headers.getheader("content-length"))
        body = self.rfile.read(clen)
        try:
            call_data = xmlrpclib.loads(body)
        except xml.parsers.expat.ExpatError:
            call_data = None
        # d = cgi.parse_qs(body) -- for later
        # -- for now, assuming always XML-RPC
        (args, funct) = call_data
        xmlrpc_bindings = {"filterData": self.xmlrpc_filterData,
                           "wiki.filterData": self.xmlrpc_filterData,
                           "cached": self.xmlrpc_cached,
                           "dump_cache": self.xmlrpc_dump_cache,
                           "validate": self.xmlrpc_validate,
                           "render": self.xmlrpc_render}
        try:
            result = xmlrpc_bindings[funct](*args)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(xmlrpclib.dumps((result,)))
        except IndexError:
            pass

    def xmlrpc_filterData(self, data, contentType, params):
        data = data.decode("utf-8", "replace")
        url = params["namespace"]
        return (localnames.replace_text(data, url), contentType)

    def xmlrpc_cached(self):
        results = []
        for url, ns in localnames.store.items():
            preferred_name = ns["X"].get("PREFERRED-NAME", ["(none)"])[0]
            ttl = int(ns["TIME"] + localnames.time_to_live - time.time())
            results.append((url, preferred_name, ttl))
        return results

    def xmlrpc_dump_cache(self, url):
        localnames.dump_cache(url)
        return 1

    def xmlrpc_validate(self, url):
        return localnames.get_namespace(url)["ERRORS"]

    def xmlrpc_render(self, format, url):
        if type(url) == type([]):
            ns = localnames.aggregate(url)
        else:
            ns = localnames.get_namespace(url)
        if format in ["XML-RPC", "XML-RPC-text"]:
            ns2 = {}
            for k in ["LN", "X", "NS", "PATTERN"]:
                ns2[k] = un_unicode_dict(ns[k])
            if format == "XML-RPC":
                return ns2
            else:
                return xmlrpclib.dumps((result,))
        elif format == "version1.1":
            return localnames.clean(ns)
        elif format == "version1.1-original":
            return ns["TEXT"]


if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(("localhost", 9000), LocalNamesHandler)
    httpd.serve_forever()

