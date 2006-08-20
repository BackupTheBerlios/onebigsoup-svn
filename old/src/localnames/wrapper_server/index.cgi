#!/usr/bin/env python
"""DOC

DOC

DOC
"""

import os
import time

import cgi
import cPickle as pickle
import urllib
import xmlrpclib

import Cheetah.Template
import cgitb
cgitb.enable(1)


WEBSERVICE_PREFIX = "http://ln.taoriver.net/wrap"


class WrapHub:

    """DOC

    DOC

    DOC
    """

    def __init__(s, pickle_filename):
        """DOC"""
        s.pickle = WrapPickle(s, pickle_filename)
        s.lists = WrapLists(s)
        s.cgidata = CgiData(s)
        s.pickle.load()

    def event_loadfromdict(s, d):
        """DOC"""
        s.lists.event_loadfromdict(d)

    def event_savetodict(s, d):
        """DOC"""
        s.lists.event_savetodict(d)
    
    def event_dirtydb(s):
        """Occurs when a change is made to the database."""
        s.pickle.event_dirtydb()


class CgiData:

    """DOC

    DOC

    DOC
    """

    def __init__( s, src ):
        """DOC"""
        s.src = src
        s.form = None
        s.path = None
        s._load_path()
        s._load_form()
        
    def _load_path(s):

        """DOC"""

        unquote = urllib.unquote
        split_on_slashes = lambda S: S.split("/")
        remove_blanks = lambda L: [x for x in L if x != ""]
        process_path = lambda x: remove_blanks(split_on_slashes(unquote(x)))
        
        path = os.environ.get("REQUEST_URI", "/")
        if path == "/index.cgi": path="/"
        path = process_path(path)
        s.path = path
        
    def _load_form(s):
        """DOC

        Note: only works 1st time!
        """
        s.form = cgi.FieldStorage()
        
    def get_path(s):
        return s.path

    def get_form(s):
        return s.form

    def keys( s ):
        return s.form.keys()

    def val( s, key_name ):
        """DOC"""
        if s.form.has_key(key_name):
            return s.form[key_name].value
        return None

    def values(s, key_names):
        """DOC

        Return a giant dictionary of key:value, as returned by val.
        """
        d = {}
        for key_name in key_names:
            d[key_name] = s.val(key_name)
        return d

    def checked(s, key_name):
        return s.val(key_name) == "on"


class WrapLists:
    def __init__( s, wrap ):
        s.wrap = wrap
        s.space_data = {}
    def event_loadfromdict( s, d ):
        s.space_data = d[ "list-bindings" ]
    def event_savetodict( s, d ):
        d[ "list-bindings" ] = s.space_data
    def bind( s, space_name, list_url, xmlrpc_url, entry_pattern, final_pattern=None, xmlrpc_namespace=None ):
        s.space_data[space_name] = {"url": list_url,
                                    "xmlrpc-url": xmlrpc_url,
                                    "xmlrpc-namespace": xmlrpc_namespace,
                                    "pattern": entry_pattern,
                                    "final": final_pattern,}
        s.wrap.event_dirtydb()
    def all_spaces(s):
        return s.space_data.keys()
    def url_for_space(s, space_name ):
        return s.space_data[space_name]["url"]
    def render_localnames(s, space_name):
        if not s.space_data.has_key(space_name):
            return '# no such space "'+space_name+'" defined'
        results = []
        data = s.space_data[space_name]
        url = data["url"]
        pattern = data["pattern"]
        final = data["final"]
        xmlrpc_url = data.get("xmlrpc-url", None)

	results.append('X "VERSION" "1.2"')
	results.append('')
        results.append('# Local Names namespace description for ' + space_name + '.')
	results.append('# This namespace was automatically generated.')
	results.append('# Learn about Local Names: http://purl.net/net/localnames/')
        results.append('')
        results.append('X "GENERATOR" "' + WEBSERVICE_PREFIX + '"')
        results.append('X "PREFERRED-NAME" "' + space_name + '"')
        iso8601 = time.strftime("%Y-%m-%d")
	results.append('X "LAST-GENERATED" "' + iso8601 + '"')
        if xmlrpc_url:
            results.append('X "FROM-WIKIRPC2-GETALLPAGES" "' + xmlrpc_url + '"')
        else:
            results.append('X "FROM-NAMES-LIST" "' + url + '"')
        results.append('X "PRODUCED-BY-PATTERN" "' + pattern + '"')
        results.append("")

        if final != None:
            results.append('X "FINAL" "%(final)s"' % locals())
            results.append("")

        if xmlrpc_url:
            server = xmlrpclib.ServerProxy(xmlrpc_url)
            xmlrpc_ns = data.get("xmlrpc-namespace", None)
            if not xmlrpc_ns:
                list_of_names = server.getAllPages()
            else:
                list_of_names = server.wiki.getAllPages()
        else:
            page = urllib.urlopen(url)
            list_of_names = [line.strip("\r\n") for line in page.readlines()]
            list_of_names = [line for line in list_of_names if line.strip() != ""]
        
        for name in list_of_names:
            names_url = pattern.replace("$NAME", name)
            results.append('LN "%(name)s" "%(names_url)s"' % locals())

        results = "\n".join(results) + "\n"
        try:
            return results.encode("utf-8","replace")
        except UnicodeDecodeError:
            return results

class WrapPickle:
    def __init__(s, wrap, filename):
        s.wrap = wrap
        s.filename = filename
        s.to_save = False
    def load(s):
        try:
            d = pickle.load(open(s.filename))
            s.wrap.event_loadfromdict(d)
        except IOError:
            pass
    def save(s):
        if not s.to_save:
            return  # only save if dirt (event_dirtydb occurs)
        d = {}
        s.wrap.event_savetodict(d)
        pickle.dump(d, open(s.filename,"w"))
    def event_dirtydb(s):
        s.to_save = True


class WrapCgiResponse:
    def __init__(s, wrap_hub):
        s.wrap = wrap_hub
        
    def text_html(s):
        print "Content-type: text/html"
        print

    def text_plain(s):
        print "Content-type: text/plain"
        print

    def front_page(s):
        s.text_html()
        template = Cheetah.Template.Template(file="front_page.tmpl")
        d=s.wrap.cgidata.values(["action", "spacename", "nameslisturl",
                                 "xmlrpcurl", "finalurlpattern",
                                 "urlpattern",])
        if d["action"] == "bind":
            spacename = d["spacename"]
            nameslisturl = d["nameslisturl"]
            xmlrpcurl = d["xmlrpcurl"]
            urlpattern = d["urlpattern"]
            finalurlpattern = d["finalurlpattern"]
            
            webservice_prefix = WEBSERVICE_PREFIX
            template.msg = """bound space <a href="%(webservice_prefix)s/%(spacename)s">&quot;%(spacename)s&quot;</a> to list <a href="%(nameslisturl)s">%(nameslisturl)s</a>""" % locals()
            if xmlrpcurl:
                template.msg = """bound space <a href="%(webservice_prefix)s/%(spacename)s">&quot;%(spacename)s&quot;</a> to list at XML-RPC url <a href="%(xmlrpcurl)s">%(xmlrpcurl)s</a> (getAllNames)""" % locals()
            template.default_spacename = spacename
            template.default_nameslisturl = nameslisturl
            template.default_xmlrpcurl = xmlrpcurl
            template.default_urlpattern = urlpattern
            template.default_finalurlpattern = finalurlpattern
            if finalurlpattern == "":
                finalurlpattern_fixed = None
            else:
                finalurlpattern_fixed = finalurlpattern

            # autodetect if the getAllPages method is in a special function
            xmlrpc_namespace = None
            if xmlrpcurl:
                server = xmlrpclib.ServerProxy(xmlrpcurl)
                try:
                    methods = server.listMethods()
                except xmlrpclib.Fault:
                    try:
                        methods = server.system.listMethods()
                    except xmlrpclib.Fault:
                        methods = None
                if methods:
                    for function_name in methods:
                        if ".getAllPages" in function_name:
                            xmlrpc_namespace = ".".join( function_name.split(".")[:-1] )
            s.wrap.lists.bind(spacename, nameslisturl, xmlrpcurl, urlpattern, finalurlpattern_fixed, xmlrpc_namespace)
        else:
            template.msg = None
            template.default_spacename = ""
            template.default_nameslisturl = "http://"
            template.default_xmlrpcurl = ""
            template.default_urlpattern = "http://...$NAME"
            template.default_finalurlpattern = ""
	template.webservice_prefix = WEBSERVICE_PREFIX
        print template

    def spaces_page(s):
        s.text_html()
        template = Cheetah.Template.Template(file="spaces_page.tmpl")
        spaces = []
        for space_name in s.wrap.lists.all_spaces():
            spaces.append({"name": space_name,
                           "url": WEBSERVICE_PREFIX + "/" + space_name})
        template.spaces = spaces
        template.webservice_prefix = WEBSERVICE_PREFIX
        print template

    def namespace_page( s, space ):
        s.text_plain()
        description = s.wrap.lists.render_localnames(space)
        print description

    def debug_page(s):
        s.text_html()
        template = Cheetah.Template.Template(file="debug_page.tmpl")
        template.webservice_prefix = WEBSERVICE_PREFIX
        template.form_info = repr(s.wrap.cgidata.keys())
        print template

    def run(s):
        """Run the right page, based on the input."""
        path = s.wrap.cgidata.get_path()
#	s.text_plain()  # TODO, NO-COMMIT
#	print path  # TODO, NO-COMMIT
        if path == ["wrap"]:
            s.front_page()
        elif path == ["wrap", "spaces"]:
            s.spaces_page()
        elif len(path)==2:
            s.namespace_page(path[1])
        else:
            s.front_page()

if __name__ == "__main__":
    wrap = WrapHub("wrap.p")
    response = WrapCgiResponse(wrap)
    response.run()
    wrap.pickle.save()
