
#
# Old code from original my.localnames.
#
# I'm pillaging the data store code from it.
# 


XMLRPC_NAMESERVER = "http://services.taoriver.net:9089/"

MAX_LOGS=100



import cPickle as pickle
import StringIO
import xmlrpclib
import time


def edit_key( space_name ):
    import code_info
    return "index.cgi?%s=%s&%s=%s" % ( code_info.PAGE_KEY, code_info.PAGE_EDITNAMES,
                                       code_info.SPACE_KEY, space_name )

def description_key( space_name ):
    import code_info
    return "index.cgi?%s=%s&%s=%s" % ( code_info.PAGE_KEY, code_info.PAGE_DESCRIPTION,
                                       code_info.SPACE_KEY, space_name )

def uli_xmlrpc( url, line ):
    return xmlrpclib.ServerProxy( url ).uli( line )


class PickleData:
    def __init__( s, hub, filename ):
        s.hub = hub
        s.filename = filename
    def load(s):
        try:
            d = pickle.load( open(s.filename) )
            s.hub.event_loadfromdict( d )
        except IOError:
            pass
    def save(s):
        d = {}
        s.hub.event_savetodict( d )
        pickle.dump( d, open(s.filename,"w") )


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
        s.log = [] # { "msg": (html), "time": (#secs-from-epoch) }
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
        # LN: mapping from LN to URL
        # NS: mapping from NS to URL
        # X: mapping from X to value
        # FINAL: value of final item
        # LN-list: list of LN keys, in order
        # NS-list: list of NS keys, in order

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


hub = DataHub()



