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
                args["lookup"] = args["path"].split("/")
            url = localnames.lookup(args["lookup"],
                                    args["namespace"][0],
                                    redir_lookup_flags)
            self.send_response(301)
            self.send_header("Location", url)
            self.end_headers()
            return
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
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
                           "cached": self.xmlrpc_cached,
                           "dump_cache": self.xmlrpc_dump_cache,
                           "validate": self.xmlrpc_validate,
                           "wiki.filterData": self.xmlrpc_filterData}
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
        return localnames.replace_text(data, url)

    def xmlrpc_cached(self):
        results = []
        for url, ns in localnames.store.items():
            preferred_name = ns["X"].get("PREFERRED-NAME", [None])[0]
            ttl = int(ns["TIME"] + localnames.time_to_live - time.time())
            results.append((url, preferred_name, ttl))
        return results

    def xmlrpc_dump_cache(self, url):
        localnames.dump_cache(url)
        return 1

    def xmlrpc_validate(self, url):
        return localnames.get_namespace(url)["ERRORS"]



if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(("localhost", 9000), LocalNamesHandler)
    httpd.serve_forever()

