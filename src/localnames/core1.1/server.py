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


redirect_lookup_flags = sets.ImmutableSet(["loose", "check-neighboring-spaces"])

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

    def respond(self, code, key, val):
        self.send_response(code)
        self.send_header(key, val)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/?"):
            args = cgi.parse_qs( self.path[2:] )
        else:
            args = {}

        if args.get("action") in [["redirect"],["lookup"]] and \
               args.get("namespace") != None and \
               args.get("lookup") != None:
            all_lookups = []
            all_urls = []
            for lookup in args["lookup"]:
                if args.has_key("separator"):
                    lookup = lookup.split(args["separator"][0])
                else:
                    lookup = [lookup]
                all_lookups.append(lookup)
                url = localnames.lookup(lookup,args["namespace"][0],
                                        redirect_lookup_flags)
                all_urls.append(url)
            if args["action"] == ["redirect"]:
                self.respond(301, u'Location', all_urls[0])
                return
            if args.has_key("html"):
                self.respond(200, u'Content-type', 'text/html; charset=utf-8')
                line = u'<a href="%s">%s</a>\n'
            else:
                self.respond(200, u'Content-type', 'text/plain; charset=utf-8')
                line = u'%s\n'
            for url in all_urls:
                if type(url) in [type(u'unicode'), type("string")]:
                    if args.has_key("html"):
                        self.wfile.write(line % (url,url))
                    else:
                        self.wfile.write(line % url)
                else:
                    self.wfile.write(url[3]+'\n')
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
            if html:
                self.respond(200, u'Content-type', 'text/html; charset=utf-8')
            else:
                self.respond(200, u'Content-type', 'text/plain; charset=utf-8')
            self.wfile.write(u'\n'.join(draw))
            return

        if args.get("action") == ["dump-cache"] and \
               args.get("namespace") != None:
            dumped = []
            for url in args["namespace"]:
                if localnames.dump_cache(url):
                    dumped.append(url)
            self.wfile.write(u'Dumped cache:\n')
            self.wfile.write(u'\n'.join(dumped))
            return

        if args.get("action") == ["validate"] and \
           args.get("namespace") != None:
            ns = localnames.get_namespace(args["namespace"][0])
            self.respond(200, u'Content-type', 'text/html; charset=utf-8')
            if len(ns["ERRORS"]) == 0:
                self.wfile.write(u'No Errors. OK!')
                return
            self.wfile.write(u'ERRORS:\n')
            for num, line in ns["ERRORS"]:
                self.wfile.write(u'%4d.  %s' % (num, line))
            return

        if args.get("action") == ["render"] and \
           args.get("namespace") != None:
            format = args.get("format", ["version1.1"])[0]
            if format == "XML-RPC":
                format = "XML-RPC-text"
            self.respond(200, u'Content-type', 'text/plain; charset=utf-8')
            if len(args["namespace"]) == 1:
                url=args["namespace"][0] # get_namespace
            else:
                url=args["namespace"] # aggregate
            self.wfile.write(self.xmlrpc_render(format, url))
            return

        if args.get("action") == ["index"] and \
           args.get("namespace") != None:
            record_type = args.get("record-type", ["LN"])[0]
            self.respond(200, u'Content-type', 'text/plain; charset=utf-8')
            for text in self.xmlrpc_index(args["namespace"], record_type):
                self.wfile.write((text+u'\n').encode('utf-8'))
            return
        
        self.respond(200, u'Content-type', 'text/html; charset=utf-8')
        
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
        form_dict = cgi.parse_qs(body)
        if call_data == None:
            self.handle_httppipe(form_dict)
            return
        (args, funct) = call_data
        xmlrpc_bindings = {"filterData": self.xmlrpc_filterData,
                           "wiki.filterData": self.xmlrpc_filterData,
                           "cached": self.xmlrpc_cached,
                           "dump_cache": self.xmlrpc_dump_cache,
                           "validate": self.xmlrpc_validate,
                           "render": self.xmlrpc_render,
                           "index": self.xmlrpc_index,
                           "lookup": self.xmlrpc_lookup}
        try:
            args = list(args)
            args[0] = str(args[0]) # hehehe
            result = xmlrpc_bindings[funct](*args)
            self.respond(200, u'Content-type', 'text/html; charset=utf-8')
            self.wfile.write(xmlrpclib.dumps((result,)))
        except IndexError:
            pass

    def handle_httppipe(self, form_dict):
        """Called by do_POST when body looks like a form post."""
        
        self.respond(200, u'Content-type', 'text/plain; charset=utf-8')
        if not form_dict.has_key("body"):
            self.wfile.write('Error: no form entry with key "body"')
            return
        if not form_dict.has_key("namespace"):
            self.wfile.write('Error: no form entry with key "namespace"')
            return
        result = localnames.replace_text(form_dict["body"][0],
                                         form_dict["namespace"][0])
        self.wfile.write(result.encode("utf-8"))

    def xmlrpc_lookup(self, path, namespace, flags):
        if type(path) == type("string"):
            paths = [[path]] # Path is a single name.
        elif type(path[0]) == type("string"):
            paths = [path]  # Path is a single path.
        else:
            paths = path  # Path is a list of paths.
        results = []
        flags = sets.ImmutableSet(flags)
        for single_path in paths:
            results.append(localnames.lookup(single_path, namespace, flags))
        if type(path) == type("string") or type(path[0]) == type("string"):
            return results[0]
        else:
            return results

    def xmlrpc_filterData(self, data, contentType, params):
        data = data.decode("utf-8", "replace")
        url = params["namespace"]
        return ({"data": xmlrpclib.Binary(localnames.replace_text(data, url).encode("utf-8")),
                 "contentType": contentType})

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
                return xmlrpclib.dumps((ns2,))
        elif format == "version1.1":
            return localnames.clean(ns)
        elif format == "original":
            return ns["TEXT"]
        elif format == "python":
            import pprint
            return pprint.pformat(ns)

    def xmlrpc_index(self, url, record_type):
        if record_type not in ["LN", "NS", "PATTERN", "X"]:
            return []
        if type(url) == type(""):
            urls = [url]
        else:
            urls = url
        response = []
        for url in urls:
            ns = localnames.get_namespace(url)
            response.extend(ns[record_type].keys())
        return response


if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(("localhost", 9001), LocalNamesHandler)
    httpd.serve_forever()

