#!/usr/bin/env python

import time
import socket
import pprint
import os
import sys

import cPickle as pickle

PATH_PREFIX = "/home/jroes/lnss/"
PATH_TO_CHERRYPY = PATH_PREFIX + "cherrypy"
MAIL = "/usr/sbin/sendmail"
HOST_NAME = "localnames.sosdg.org"
PORT_NUMBER = 9001
USERS_DB = PATH_PREFIX + "users.p"
WEB_DIR = "/home/jroes/public_html/"
URL_PREFIX = "http://localnames.sosdg.org/"

from cherrypy import cpg
import cherrypy.lib.filter.xmlrpcfilter

UserDoesntExistError = -1
NamespaceDoesntExistError = -2
AccessDeniedError = -3
UserAlreadyExistsError = -4
IncorrectPasswordError = -5
NamespaceExistsError = -6
EntryDoesntExistError = -7

"""Quick notes:
Design to comply with V3 of the LNSS Interface Specification
http://onebigsoup.wiki.taoriver.net/moin.cgi/LocalNamesStoreXmlRpcInterface

references:
http://www.cherrypy.org/wiki/XmlRpcFilter
http://www.cherrypy.org/wiki/CherryPyTutorial
"""

class Server:
    _cpFilterList = [cherrypy.lib.filter.xmlrpcfilter.XmlRpcFilter()]
    
    def _log(s, logstring):
        """Log an operation to the screen/logfile."""
        print time.asctime(), logstring
        return True

    def _opendb(s):
        """Open database."""
        try:
            s.userlist = pickle.load( open(USERS_DB, 'r') )
        except:
            s._log("--- User database doesn't exist, creating a new one.")
            s.userlist = { }

        s._log('--- Opened database: %s' % (USERS_DB,))

        return True

    def _savedb(s):
        """Save database."""
        pickle.dump( s.userlist, open(USERS_DB, 'w') )
        s._log('--- Saved database: %s' % (USERS_DB,))
        return True

    def _save_namespace(s, username, namespace_name):
        """Create a LocalNames description and pop it into a file."""
        f = open(WEB_DIR + username + "-" + namespace_name, 'w')
        f.write("X VERSION 1.1\n")
        for entry in s.userlist[username][namespace_name]:
            f.write(entry[0] + " \"" + entry[1] + "\" \"" + entry[2] + "\"\n")

        f.close()

    def get_namespace(s, username, namespace):
        """Retrieve user's namespace file."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif not s.userlist[username].has_key(namespace):
            return NamespaceDoesntExistError
        elif namespace == "_password" or namespace == "_email":
            return AccessDeniedError
        else:
            return open(WEB_DIR + username + "-" + namespace_name, 'w').read()

    def __init__( s ):
        s._opendb()

    def _cpOnError(self):
        import traceback, StringIO
        bodyFile = StringIO.StringIO()
        traceback.print_exc(file = bodyFile)
        errorBody = bodyFile.getvalue()        
        if cpg.request.isRPC: ## this is set by the filter on xml-rpc requests
            ## convert the traceback to a dumped Fault object: the XML-RPC exception
            import xmlrpclib
            cpg.response.body = [xmlrpclib.dumps(xmlrpclib.Fault(1,errorBody))]
        else:
            ## handle regular web errors
            cpg.response.body = ['<pre>%s</pre>' % errorBody]

    def create_user(s, username, email, pw):
        """Create new user."""
        if s.userlist.has_key(username):
            return UserAlreadyExistsError
        else:
            s.userlist[username] = { }
            s.userlist[username]['_password'] = pw
            s.userlist[username]['_email'] = email

        s._log('New user: "%s"' % username)
        s._savedb()
        return True
    create_user.exposed = True

    def delete_user(s, username, pw):
        """Delete user."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            del s.userlist[username]

        s._log('Deleted user: "%s"' % username)
        s._savedb()
        return True
    delete_user.exposed = True

    def email_pw(s, username, email):
            """Email user's password to them."""
            if not s.userlist.has_key(username):
                return UserDoesntExistError
            else:
                message = "To: " + email + "\n"
                message += "From: localnames\n"
                message += "Subject: password for localnames " + HOST_NAME + ":" + str(PORT_NUMBER) + "\n\n"
                message += "Your password is " + s.userlist[username]['password'] + "\n"
                p = os.popen("%s -t" % MAIL, 'w')
                p.write(message)
                exitcode = p.close()
                return True
    email_pw.exposed = True

    def change_password(s, username, old_pw, new_pw):
        """Change user's password."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != old_pw:
            return IncorrectPasswordError
        else:
            s.userlist[username]['_password'] = new_pw
            s._savedb()
            return True

    def create_namespace(s, username, pw, namespace_name):
        """Create namespace."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif s.userlist[username].has_key(namespace_name):
            return NamespaceExistsError
        else:
            s.userlist[username][namespace_name] = [ ]
            return True

    def delete_namespace(s, username, pw, namespace_name):
        """Delete namespace."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == "_password":
            return AccessDeniedError
        elif s.userlist[username].has_key(namespace_name):
            del s.userlist[username][namespace_name]
            s._savedb()
            return True
        else:
            return NamespaceDoesntExistError

    def set(s, username, pw, namespace_name, entry_type, key, value):
        """Bind name to URL."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == '_password':
            return AccessDeniedError
        elif s.userlist[username].has_key(namespace_name):
            s.userlist[username][namespace_name].append( (entry_type, key, value) )
            f = open(WEB_DIR + username + "-" + namespace_name, 'w')
            f.write("X VERSION 1.1\n")
            for entry in s.userlist[username][namespace_name]:
                f.write(entry[0] + " \"" + entry[1] + "\" \"" + entry[2] + "\"\n")
            f.close()
            s._savedb()
            return True
        else:
            return NamespaceDoesntExistError

    def unset(s, username, pw, namespace_name, entry_type, key, value):
        """Unset namespace entry."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == '_password':
            return AccessDeniedError
        elif s.userlist[username].has_key(namespace_name):
            try:
                s.userlist[username][namespace_name].remove( (entry_type, key, value) )
                f = open(WEB_DIR + username + "-" + namespace_name, 'w')
                f.write("X VERSION 1.1\n")
                for entry in s.userlist[username][namespace_name]:
                    f.write(entry[0] + " \"" + entry[1] + "\" \"" + entry[2] + "\"\n")
                f.close()
                s._savedb()
                return True
            except:
                return EntryDoesntExistError
        else:
            return NamespaceDoesntExistError

    def get_namespaces(s, username, pw):
        """Return list of namespaces."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            namespace_list = ""
            for user in s.userlist.keys():
                for namespace in s.userlist[user].keys():
                    if not namespace.startswith("_"):
                        namespace_list = namespace_list + namespace + '\n'
            return namespace_list

    def get_server_info(s, username, pw):
        """Return information about the server."""
        return { 'INTERFACE': 'v1 Local Names Store Interface', 'IMPLEMENTATION': 'JROES-LNS-D3-V1', 'SUPPORTS_PRIVATE_NAMESPACES': 0, 'URL_NAME_PATTERN': '' }

    def get_namespace_url(s, username, pw, namespace_name):
        """Retrieve user's namespace."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == '_password':
            return AccessDeniedError
        elif s.userlist[username].has_key(namespace_name):
            return URL_PREFIX + username + "-" + namespace_name
        else:
            return NamespaceDoesntExistError

    def default(s, username, function, password, *args):
        if (function == "get_server_info"):
            return s.get_server_info(username, password)
        elif (function == "change_password"):
            return s.change_password(username, password, args[0])
        elif (function == "create_namespace"):
            return s.create_namespace(username, password, args[0])
        elif (function == "delete_namespace"):
            return s.delete_namespace(username, password, args[0])
        elif (function == "get_namespace_url"):
            return s.get_namespace_url(username, password, args[0])
        elif (function == "get_namespaces"):
            return s.get_namespaces(username, password)
        elif (function == "set"):
            return s.set(username, password, args[0], args[1], args[2], args[3])
        elif (function == "unset"):
            return s.unset(username, password, args[0], args[1], args[2], args[3])
        else:
            return "What happened?"
    default.exposed = True


cpg.root = Server()
cpg.server.start(configFile="lnss-server.conf")
