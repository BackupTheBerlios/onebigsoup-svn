#!/usr/bin/env python2.3

import cPickle as pickle
import os
import cgi
import sys
import urllib
import Cheetah.Template
import lnparser
import StringIO
import xmlrpclib
import time


import cgitb
cgitb.enable(1)

ADMIN_PASSWORD = "password"
XMLRPC_NAMESERVER = "http://services.taoriver.net:9089/"
WEBSERVICE_PREFIX = "http://my.localnames.taoriver.net"
DUMP_ADDRESS = "http://localnames.taoriver.net/dump/"

MAX_LOGS=100

NEW_KEY = "new"
ACTIVITY_KEY = "activity"
SPACES_KEY = "spaces"
ADMIN_KEY = "admin" + ADMIN_PASSWORD

EDIT_KEY = "edit"
PROTECT_KEY = "protect"
IMPORT_KEY = "import"
DESCRIPTION_KEY = "description"

DEFAULT_KEY = NEW_KEY # start on the "new" page


NEW_PAGE = WEBSERVICE_PREFIX + "/" + NEW_KEY + "/"
ACTIVITY_PAGE = WEBSERVICE_PREFIX + "/" + ACTIVITY_KEY + "/"
SPACES_PAGE = WEBSERVICE_PREFIX + "/" + SPACES_KEY + "/"
ADMIN_PAGE = WEBSERVICE_PREFIX + "/" + ADMIN_KEY + "/"

def load_up_template( tmpl ):
    tmpl.webservice_prefix = WEBSERVICE_PREFIX
    tmpl.new_page = NEW_PAGE
    tmpl.activity_page = ACTIVITY_PAGE
    tmpl.spaces_page = SPACES_PAGE
    tmpl.admin_page = ADMIN_PAGE
    tmpl.debug = None

def edit_key(space_name):
    return WEBSERVICE_PREFIX + "/" + SPACES_KEY + "/" + space_name + "/" + EDIT_KEY + "/"

def protect_key(space_name):
    return WEBSERVICE_PREFIX + "/" + SPACES_KEY + "/" + space_name + "/" + PROTECT_KEY + "/"

def import_key(space_name):
    return WEBSERVICE_PREFIX + "/" + SPACES_KEY + "/" + space_name + "/" + IMPORT_KEY + "/"

def description_key(space_name):
    return WEBSERVICE_PREFIX + "/" + SPACES_KEY + "/" + space_name + "/" + DESCRIPTION_KEY + "/"

def load_up_template_for_space( tmpl, space_name ):
    load_up_template( tmpl )
    tmpl.space_name = space_name
    tmpl.edit_page = edit_key(space_name)
    tmpl.protect_page = protect_key(space_name)
    tmpl.import_page = import_key(space_name)
    tmpl.description_page = description_key(space_name)


def uli_http( url, line ):
    return urllib.urlopen( url, urllib.urlencode( {"ULI":line} ) ).read()

def uli_xmlrpc( url, line ):
    return xmlrpclib.ServerProxy( url ).uli( line )


class PickleData:
    def __init__( s, src, filename ):
        s.src = src
        s.filename = filename
    def load(s):
        try:
            d = pickle.load( open(s.filename) )
            s.src.event_loadfromdict( d )
        except IOError:
            pass
    def save(s):
        d = {}
        s.src.event_savetodict( d )
        pickle.dump( d, open(s.filename,"w") )

class CgiData:
    def __init__( s, src ):
        s.src = src
        s.form = None
        s.path = None
        s._load_path()
        s._load_form()
        
    def _load_path(s):
        unquote = urllib.unquote
        split_on_slashes = lambda S: S.split("/")
        remove_blanks = lambda L: [x for x in L if x != ""]
        process_path = lambda x: remove_blanks(split_on_slashes(unquote(x)))
        
        path = os.environ.get( "REQUEST_URI", "/" )
        if path == "/index.cgi": path="/"
        path = process_path( path )
        s.path = path
        
    def _load_form(s):
        """
        Note: only works 1st time!
        """
        s.form = cgi.FieldStorage()
        
    def get_path(s):
        return s.path
    def get_form(s):
        return s.form

    def val( s, key_name ):
        if s.form.has_key( key_name ):
            return s.form[ key_name ].value
        return None
    def values( s, key_names ):
        """
        return giant dictionary of key:value
        as returned by val
        """
        d = {}
        for key_name in key_names:
            d[ key_name ] = s.val( key_name )
        return d
    def checked( s, key_name ):
        return s.val( key_name ) == "on"

class DataHub:
    def __init__( s ):
        s.pickle = PickleData( s, "data.p" )
        s.activity_log = ActivityLog( s )
        s.space_notes = SpacesNotes( s )
        s.namespace_files = NameSpaceFiles( s )
        s.xmlrpcserver_notification = XmlRpcServerNotification( s )
        s.pickle.load()
    def event_loadfromdict( s, d ):
        s.space_notes.event_loadfromdict(d)
        s.activity_log.event_loadfromdict(d)
    def event_savetodict( s, d ):
        s.space_notes.event_savetodict(d)
        s.activity_log.event_savetodict(d)
    def event_newspace( s, space_name ):
        s.namespace_files.event_newspace( space_name )
        s.activity_log.event_newspace( space_name )
    def event_namesadded( s, space_name, new_names, new_url ):
        s.activity_log.event_namesadded( space_name, new_names, new_url )
        s.xmlrpcserver_notification.event_namesadded( space_name, new_names, new_url )
    def event_namespacesadded( s, space_name, new_names, new_url ):
        s.activity_log.event_namespacesadded( space_name, new_names, new_url )
        s.xmlrpcserver_notification.event_namespacesadded( space_name, new_names, new_url )

class XmlRpcServerNotification:
    def __init__( s, datahub ):
        s.datahub = datahub
    def tell_dump(s, space_name):
        uli_xmlrpc( XMLRPC_NAMESERVER, "dump-cache %s" % description_key( space_name ) )
    def event_namesadded( s, space_name, new_names, new_url ):
        s.tell_dump( space_name )
    def event_namespacesadded( s, space_name, new_names, new_url ):
        s.tell_dump( space_name )
    
class ActivityLog:
    def __init__( s, datahub ):
        s.datahub = datahub
        s.log = []
    def event_loadfromdict( s, d ):
        s.log = d.get( "log", [] )
    def event_savetodict( s, d ):
        d[ "log" ] = s.log
    def note( s, msg ):
        s.log.insert( 0, {"msg":msg,
                          "time":time.time()} )
        if len( s.log ) > MAX_LOGS:
            s.log=s.log[:MAX_LOGS]
    def get_logs( s, n=MAX_LOGS ):
        return s.log[:n]
    def event_newspace( s, space_name ):
        s.note( "new space: %s" % space_name )
    def event_namesadded( s, space_name, new_names, new_url ):
        s.note( '<a href="%s">%s</a>- added: ' % (edit_key(space_name),space_name) + ", ".join( ['<a href="%s">%s</a>' % (new_url, new_name) for new_name in new_names] ) )
    def event_namespacesadded( s, space_name, new_names, new_url ):
        s.note( '<a href="%s">%s</a>- added namespace: ' % (edit_key(space_name),space_name) + ", ".join( ['<a href="%s">%s</a>' % (new_url, new_name) for new_name in new_names] ) )

class NameSpaceFiles:
    def __init__( s, datahub ):
        s.datahub = datahub
    def get_space( s, name ):
        nsf = NameSpaceFile( s.datahub, name )
        nsf.load()
        return nsf
    def event_newspace( s, space_name ):
        nsf = NameSpaceFile( s.datahub, space_name )
        nsf.add_name( "this", description_key( space_name ) )
        nsf.add_name( "edit", edit_key( space_name ) )
        nsf.add_name( "my.localnames", WEBSERVICE_PREFIX + "/" )
        nsf.add_name( "dump", DUMP_ADDRESS )
        nsf.save()

class NameSpaceFile:
    def __init__( s, datahub, name ):
        s.datahub = datahub
        s.name = name
        s.filename = "data/" + name + ".p"
        s.data = {"LN":{}, "NS":{}, "X":{}, "FINAL":None, "LN-list":[], "NS-list":[] }

    def load(s):
        try:
            s.data = pickle.load(open(s.filename))
        except IOError:
            pass

    def save(s, pword = None ):
        if not s.datahub.space_notes.check_password( s.name, pword ):
            return False
        pickle.dump(s.data, open(s.filename, "w"))
        return True

    def get_contents(s):
        file = StringIO.StringIO()
        for key in s.data["LN-list"]:
            file.write( 'LN "%s" "%s"\n' % (key,s.data["LN"][key]) )
        for key in s.data["NS-list"]:
            file.write( 'NS "%s" "%s"\n' % (key,s.data["NS"][key]) )
        for key in s.data["X"]:
            file.write( 'X "%s" "%s"\n' % (key,s.data["X"][key]) )
        if s.data["FINAL"]:
            file.write( 'FINAL "%s" -\n' % s.data["FINAL"] )
        file.seek(0)
        return file.read()


    def get_names(s):
        return s.data["LN"]

    def get_names_in_order(s):
        return [(name,s.data["LN"][name]) for name in s.data["LN-list"]]

    def get_namespaces(s):
        return s.data["NS"]

    def get_namespaces_in_order(s):
        return [(name,s.data["NS"][name]) for name in s.data["NS-list"]]

    def get_extensiondata(s):
        return s.data["X"]

    def get_final(s):
        return s.data["FINAL"]

    def add_name( s, name, url ):
        s.data["LN"][ name ] = url
        if name not in s.data[ "LN-list" ]:
            s.data[ "LN-list" ].append( name )

    def add_names( s, names, url ):
        for name in names:
            s.add_name( name, url )

    def has_name( s, name ):
        return s.data[ "LN" ].has_key( name )

    def add_namespace( s, namespace, url ):
        s.data["NS"][ namespace ] = url
        if namespace not in s.data["NS-list"]:
            s.data["NS-list"].append(namespace)
                
    def add_namespaces( s, namespaces, url ):
        for namespace in namespaces:
            s.add_namespace( namespace, url )

    def has_namespace( s, namespace ):
        return s.data[ "NS" ].has_key( namespace )

    def add_extension( s, key, val ):
        s.data["X"][ key ] = val

    def set_final( s, pattern ):
        s.data["FINAL"] = pattern

    def delete_name(s, name):
        del s.data["LN"][name]
	s.data["LN-list"].remove( name )

    def delete_namespace(s, name):
        del s.data["NS"][name]
	s.data["NS-list"].remove( name )

    def delete_url(s, url):
        for name in s.data["LN"]:
            if s.data["LN"][name]==url:
		s.delete_name( name )
        for namespace in s.data["NS"]:
            if s.data["NS"][namespace]==url:
		s.delete_namespace( namespace )

class ForeignNameSpace:
    def __init__( s, url ):
        s.url = url
        server = xmlrpclib.ServerProxy( XMLRPC_NAMESERVER )
        s.data = server.parse_description( url )
    def load_names_into_namespace_file( s, nsf, overwrite=False ):
        for name in s.data[ "LN" ]:
            if overwrite == False and nsf.has_name( name ):
                continue
            nsf.add_name( name, s.data["LN"][name] )
    def load_namespaces_into_namespace_file( s, nsf, overwrite=False ):
        for name in s.data[ "NS" ]:
            if overwrite == False and nsf.has_namespace( name ):
                continue
            nsf.add_namespace( name, s.data["NS"][name] )

class SpacesNotes:
    def __init__( s, datahub ):
        s.datahub = datahub
        s.spaces = {}
    def event_loadfromdict( s, d ):
        s.spaces = d[ "space-notes" ]
    def event_savetodict( s, d ):
        d[ "space-notes" ] = s.spaces
    def space_titles( s ):
        return s.spaces.keys()
    def create_space( s, name ):
        if s.spaces.has_key( name ):
            return False
        s.spaces[ name ] = { "name": name,
                             "password": None }
        s.datahub.event_newspace( name )
        return True
    def has_password( s, space_name ):
        try:
            return s.spaces[ space_name ][ "password" ] != None
        except KeyError:
            return False
    def check_password( s, space_name, pw ):
        try:
            if s.spaces[ space_name ][ "password" ] == None:
                return True
            return s.spaces[ space_name ][ "password" ] == pw
        except KeyError:
            return True
    def set_password( s, space_name, old_pw, new_pw ):
        if not s.check_password( space_name, old_pw ):
            return False
        s.spaces[ space_name ][ "password" ] = new_pw
        return True

class WebSite:
    def __init__( s, datahub ):
        s.datahub = datahub
        s.cgidata = CgiData(s)

    def text_html(s):
        print "Content-type: text/html"
        print

    def text_plain(s):
        print "Content-type: text/plain"
        print

    def redirect_browser(s, url):
        print "Location:", url
        print

    def new_page(s):
        s.text_html()
        template = Cheetah.Template.Template( file = "new_page.tmpl" )
        load_up_template( template )
        print template

    def activity_page(s):
        s.text_html()
        template = Cheetah.Template.Template( file = "activity_page.tmpl" )
        load_up_template( template )
        logs = [x.copy() for x in s.datahub.activity_log.get_logs()]
        for log in logs:
            log[ "humantime" ] = time.asctime( time.gmtime( log[ "time" ] ) )
        template.logs = logs
        print template

    def spaces_page(s):
        s.text_html()
        template = Cheetah.Template.Template( file = "spaces_page.tmpl" )
        load_up_template( template )

        data = [{"title":title,
                 "url":edit_key(title)} for title in s.datahub.space_notes.space_titles()]
        template.space_data = data
        
        print template

    def description_page(s, space_name):
        s.text_plain()

        nsf=s.datahub.namespace_files.get_space(space_name)
        print nsf.get_contents()
    
    def import_page( s, space_name ):
        s.text_html()

        form = s.cgidata.get_form()

        template = Cheetah.Template.Template( file="import_page.tmpl" )
        load_up_template_for_space( template, space_name )

        template.processing = None
        template.say_invalid_pw=0

        vals = [ "action", "nameurl", "password" ]
        d = s.cgidata.values( vals )
        valid_pw = s.datahub.space_notes.check_password( space_name, d["password"] )
        if d["action"] == "import":
            template.processing = 1

            nameurl = d[ "nameurl" ]
            allnames = s.cgidata.checked( "allnames" )
            allnamespaces = s.cgidata.checked( "allnamespaces" )
            overwrite = s.cgidata.checked( "overwrite" )

            template.nameurl = nameurl
            template.allnames = allnames
            template.allnamespaces = allnamespaces
            template.overwrite = overwrite

            if valid_pw:
                nsf = s.datahub.namespace_files.get_space( space_name )
                fns = ForeignNameSpace( nameurl )
                if allnames:
                    fns.load_names_into_namespace_file( nsf, overwrite )
                if allnamespaces:
                    fns.load_namespaces_into_namespace_file( nsf, overwrite )
                nsf.save( d["password"] )
            else:
                template.say_invalid_pw=1

        template.has_password=s.datahub.space_notes.has_password( space_name )
        print template

    def protect_page( s, space_name ):
        s.text_html()
        form = s.cgidata.get_form()

        template = Cheetah.Template.Template( file = "protect_page.tmpl" )
        template.debug = None

        if form.has_key( "action" ) and form["action"].value == "Submit":
            template.processing=True
            pw = s.cgidata.val( "password" )
            pw1 = s.cgidata.val( "password1" )
            pw2 = s.cgidata.val( "password2" )

            if not s.datahub.space_notes.check_password( space_name, pw ):
                template.passed = False
            else:
                template.passed = True
                if pw1!=pw2:
                    template.password_match=False
                else:
                    template.password_match=True
                    if pw1 == "":
                        pw1=None
                        pw2=None
                    s.datahub.space_notes.set_password( space_name, pw, pw1 )
        else:
            template.processing=False

        load_up_template_for_space( template, space_name )
        template.has_password=s.datahub.space_notes.has_password( space_name )
        print template
        
    def edit_page(s, space_name ):
        s.text_html()
        
        form = s.cgidata.get_form()
        nsf = s.datahub.namespace_files.get_space( space_name )
        template = Cheetah.Template.Template( file = "edit_page.tmpl" )
        template.debug = None
        template.say_invalid_pw = 0 # set to 1 if found bad, and worth showing

        vals = [ "action", "password", "namestoaddlist", "nameurl",
                 "nameorspace", ]
        d = s.cgidata.values( vals )
        valid_pw = s.datahub.space_notes.check_password( space_name, d["password"] )

        if d["action"] == "Submit":
            new_names = d["namestoaddlist"].splitlines()
            new_url = d["nameurl"]
            
            if valid_pw:
                if d["nameorspace"] == "addnames":
                    nsf.add_names( new_names, new_url )
                    s.datahub.event_namesadded( space_name, new_names, new_url )
                if d["nameorspace"] == "addnamespaces":
                    nsf.add_namespaces( new_names, new_url )
                    s.datahub.event_namespacesadded( space_name, new_names, new_url )
                nsf.save( d["password"] )
                template.saved_names = 1
            else:
                template.say_invalid_pw = 1
        elif d["action"] == "Delete":
            if valid_pw:
                for key in form:
                    if form[key].value=="on":
                        if key.startswith("ln"):
                            nsf.delete_name(key[3:])
                        elif key.startswith("ns"):
                            nsf.delete_namespace(key[3:])
                        else:
                            raise "Invalid key %s" % key
                nsf.save( d["password"] )
            else:
                template.say_invalid_pw = 1

        load_up_template_for_space( template, space_name )
        template.names = []
        template.namespaces = []
        for (name, url) in nsf.get_names_in_order():
            template.names.append( { "name": name, "url": url } )
        for (name, url) in nsf.get_namespaces_in_order():
            template.namespaces.append( {"name": name, "url": url } )
        template.has_password=s.datahub.space_notes.has_password( space_name )
        print template

    def run(s):
        """
        Run the right page, based on the input.
        """
        path = s.cgidata.get_path()
        if path == [NEW_KEY]:
            if s.cgidata.get_form().has_key( "space" ):
                space_name = s.cgidata.get_form()[ "space" ].value
                s.datahub.space_notes.create_space( space_name )
                s.redirect_browser(edit_key(space_name))
            else:
                s.new_page()
        elif path == [ACTIVITY_KEY]:
            s.activity_page()
        elif path == [SPACES_KEY]:
            s.spaces_page()
        elif len(path)==0:
            s.new_page()
        elif path[0]==SPACES_KEY:
            space = path[1]
            if len(path)==2:
                path.append(EDIT_KEY)
            if path[2]==EDIT_KEY:
                s.edit_page(space)
            elif path[2]==DESCRIPTION_KEY:
                s.description_page(space)
            elif path[2]==PROTECT_KEY:
                s.protect_page(space)
            elif path[2]==IMPORT_KEY:
                s.import_page(space)
            else:
                s.edit_page(space)


if __name__ == "__main__":
    data = DataHub()
    site = WebSite( data )
    site.run()
    data.pickle.save()


