#!/usr/bin/env python2.3
"""
A LocalNames redirection services.

INPUTS:

  FORM:
  "action" : "bind"  -- make a redirection binding
  "spacename" : (name of space, no spaces, no dashes)
  "localnamesdescription" : (url of localnames description)

  "action" : "dump"  -- dump cache
  "spacename" : (name of space, or URL of space)

  URL ("REQUEST_URI")
  /                         -- determine action based on FORM input
  /space/subspace/.../word  -- perform a lookup

APACHE BINDING:

  Apache should rewrite every URL to /index.cgi.

INSTALLATION REQUIREMENTS:

  You need:
  * Python2.3 & Cheetah Templates (http://cheetahtemplate.org/)
  * this script & associated .tmpl files
  * mod_rewrite, and mod_rewrite instruction below installed (.htaccess)
  * the address of a LocalNames XML-RPC resolver
       FEEL FREE TO USE: http://services.taoriver.net:9090/

.htaccess

DirectoryIndex index.cgi
Options -MultiViews
RewriteEngine on
RewriteBase /
RewriteRule ^(.+)$ index.cgi [L]

You can also put these instructions in an httpd.conf virtual
host directory directive.
"""

import os
import sys
import cgi
import Cheetah.Template
import pickle
import xmlrpclib
import urllib

import cgitb; cgitb.enable()


# global settings
URL_PREFIX = "http://localnames.taoriver.net"
PICKLE_FILENAME = "bindings.p"
XMLRPC_LOCALNAMESRESOLVER_URL = "http://services.taoriver.net:9090/"


class Bindings( dict ):
    def __init__( s ):
        try:
            s.bindings = pickle.load( open(PICKLE_FILENAME) )
        except IOError:
            s.bindings = {}
        s.update( s.bindings )
    def __setitem__( s, k, v ):
        s.bindings[ k ] = v
        pickle.dump( s.bindings, open( PICKLE_FILENAME, "w" ) )

# convenience functions for response
def say_text_html():
    print "Content-type: text/html"
    print

def say_redirect_to( url ):
    print "Location: %s" % url
    print

def front_page():
    say_text_html()
    t = Cheetah.Template.Template( file="front_page.tmpl" )
    t.url_prefix = URL_PREFIX
    print t
    return

def bind( space_name, description_url ):
    say_text_html()

    bindings = Bindings()
    bindings[ space_name ] = description_url
    
    t = Cheetah.Template.Template( file="bind.tmpl" )
    t.url_prefix = URL_PREFIX
    t.space_name = space_name
    t.description_url = description_url
    print t
    return

def dump_cache_display():
    say_text_html()

    t = Cheetah.Template.Template( file="dump_cache.tmpl" )
    t.url_prefix = URL_PREFIX
    print t
    return

def perform_dump( to_dump ):
    say_text_html()

    if not to_dump.startswith( "http://" ):
        namespace_url = Bindings()[ to_dump ]
    else:
        namespace_url = to_dump

    server = xmlrpclib.ServerProxy( XMLRPC_LOCALNAMESRESOLVER_URL )

    result = server.uli( "dump-cache %s" % namespace_url )
    
    t = Cheetah.Template.Template( file="perform_dump.tmpl" )
    t.response = result
    t.url_prefix = URL_PREFIX
    if result == "Dumping cache by ULI has been turned off.":
        t.response = "Cache dumps forbidden by admin."
    elif result.endswith( "wasn't cached." ):
        t.response = "%s wasn't cached." % to_dump
    elif result.startswith( "Cache dumped for namespace by URL " ):
        t.response = "%s's cache successfully dumped." % to_dump
    print t
    return

def about():
    say_text_html()
    
    t = Cheetah.Template.Template( file="about.tmpl" )
    t.url_prefix = URL_PREFIX
    print t
    return

def namespace_file_doesnt_load( binding_point, namespace_url ):
    say_text_html()

    t = Cheetah.Template.Template( file="err_namespace_not_loading.tmpl" )
    t.binding_point = binding_point
    t.namespace_url = namespace_url
    t.url_prefix = URL_PREFIX
    print t
    return

def not_found( namespace_url, path ):
    say_text_html()

    t = Cheetah.Template.Template( file="not_found.tmpl" )
    t.path = ", ".join( ['"%s"' % x for x in path[1:]] )
    t.binding_point = path[0]
    t.word = path[-1]
    t.namespace_url = namespace_url
    t.url_prefix = URL_PREFIX
    print t
    return
    
def redirect_to( path ):
    binding_point = path[0]

    bindings = Bindings()

    namespace_url = bindings.get( binding_point, None )

    if namespace_url == None:
        return no_such_binding_point( binding_point )

    if len(path)==1:
        say_redirect_to( namespace_url )
    
    lookupserver = xmlrpclib.ServerProxy( XMLRPC_LOCALNAMESRESOLVER_URL )
    result_url = lookupserver.lookup( namespace_url, path[1:], 1 )

    if result_url == "NAMESPACE-FILE-DOESNT-LOAD":
        return namespace_file_doesnt_load( binding_point, namespace_url )
    if result_url == "NAMESPACE-NOT-FOUND":
        return namespace_not_found()
    if result_url == "NOT-FOUND":
        return not_found( namespace_url, path )
    
    say_redirect_to( result_url )
    return

def uli_response( line ):
    cgitb.enable(0)
    say_text_html()
    line = line.strip()
    if line == "ping": print "pong"; return
    if line == "whoareyou": print "LocalNames HTTP-CGI Forwarding Service ULI Port"; return
    if line == "frametype": print "Custom HTTP-CGI ULI Port"; return
    if line == "whoareyou-data": print "not implemented"; return
    if line == "help": print "commands: help, keys, val (key), set (key) (url), look (key) (space) (subspace)... (word), dump-cache (key), dump-cache (url)"; return
    if line == "keys": print " ".join( Bindings().keys() ); return
    if line.startswith( "val" ): print Bindings()[ line.split()[1] ]; return
    if line.startswith( "set" ): (key,url)=line.split()[1:]; Bindings()[key] = url; print key,"-->",url; return
    if line.startswith( "look" ):
        import shlex
        tokens = shlex.split(line)
        space = tokens[1]
        path = tokens[2:]
        namespace_url = Bindings()[space]

        lookupserver = xmlrpclib.ServerProxy( XMLRPC_LOCALNAMESRESOLVER_URL )
        result = lookupserver.lookup( namespace_url, path, 1 )
        print result
        return
    if line.startswith( "dump-cache" ):
        # call the XML-RPC LocalNames resolver, and ask it to dump cache by ULI
        (cmd,target) = line.split()
        if not target.startswith( "http://" ):
            target = Bindings()[target]
        server = xmlrpclib.ServerProxy( XMLRPC_LOCALNAMESRESOLVER_URL )
        print server.uli( "dump-cache %s" % target )
        return
    print "Don't know how to handle:",line
    return

if __name__ == "__main__":
    unquote = urllib.unquote
    split_on_slashes = lambda S: S.split("/")
    remove_blanks = lambda L: [x for x in L if x != ""]
    process_path = lambda x: remove_blanks(split_on_slashes(unquote(x)))

    # Determine what the user wants to do.
    path = os.environ.get( "REQUEST_URI", "/" )
    if path == "/index.cgi": path="/"
    path = process_path( path )

    form = cgi.FieldStorage()
    
    
    if path != []:
        if path[0].upper() == "DUMP":
            if form.has_key( "action" ) and form[ "action" ].value == "dump":
                perform_dump( form[ "spacename" ].value )
            else:
                dump_cache_display()
        elif path[0].upper() == "ULI":
            uli_response(form["ULI"].value)
        elif path[0].upper() == "ABOUT":
            about()
        else:
            redirect_to( path )
    elif form.has_key( "action" ) and form[ "action" ].value == "bind":
        bind( form[ "spacename" ].value, form[ "localnamesdescription" ].value )
    else:
        front_page()
