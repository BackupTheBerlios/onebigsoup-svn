#!/usr/bin/env python

import time
import socket
import pprint
import xmlrpclib
import os
import sys

from DocXMLRPCServer import DocXMLRPCServer
import cPickle as pickle

PATH_PREFIX = "/home/jroes/lnss/"
PATH_TO_CHERRYPY = PATH_PREFIX + "cherrypy"
MAIL = "/usr/sbin/sendmail"
HOST_NAME = "localnames.sosdg.org"
PORT_NUMBER = 9001
USERS_DB = PATH_PREFIX + "users.p"
WEB_DIR = "/home/jroes/public_html/"
URL_PREFIX = "http://localnames.sosdg.org/"

sys.path.append(PATH_TO_CHERRYPY)
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

    def delete_user(s, username, pw):
        """Delete user."""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            del s.userlist[username]

        s._log('Deleted user: "%s"' % email)
        s._savedb()
        return True

    def email_pw(s, username, email):
            """Email user's password to them"""
            if not s.userlist.has_key(username):
                return UserDoesntExistError
            else:
                message = "To: " + email + "\n"
                message += "From: localnames\n"
                message += "Subject: password for localnames " + HOST_NAME + ":" + str(PORT_NUMBER) + "\n\n"
                message += "Your password is " + s.userlist[email]['password'] + "\n"
                p = os.popen("%s -t" % MAIL, 'w')
                p.write(message)
                exitcode = p.close()
                return True

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
        """Create namespace"""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif s.userlist[username].has_key(namespace_name):
            return NamespaceExistsError
        else:
            s.userlist[username][namespace_name] = { }
            return True

    def delete_namespace(s, username, pw, namespace_name):
        """Delete namespace"""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[email]['_password'] != pw:
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
        """Bind name to URL"""
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
        """Unset namespace entry"""
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
        """Return list of namespaces"""
        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif s.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            namespace_list = ""
            for user in s.userlist:
                for namespace in user:
                    namespace_list = namespace_list + namespace + "\n"
            return namespace_list

    def get_server_info(s, username, pw):
        """Return information about the server."""
        return { 'INTERFACE': 'v1 Local Names Store Interface', 'IMPLEMENTATION': 'JROES-LNS-D3-V1', 'SUPPORTS_PRIVATE_NAMESPACES': 0, 'URL_NAME_PATTERN': '' }

    def get_namespace_url(s, username, pw, namespace_name):
        """Retrieve user's namespace"""
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
        default.exposed = True

        if not s.userlist.has_key(username):
            return UserDoesntExistError
        elif (function == "get_server_info"):
            return get_server_info(username, password)
        elif (function == "change_password"):
            return change_password(username, password, args[0])
        elif (function == "create_namespace"):
            return create_namespace(username, password, args[0])
        elif (function == "delete_namespace"):
            return delete_namespace(username, password, args[0])
        elif (function == "get_namespace_url"):
            return get_namespace_url(username, password, args[0])
        elif (function == "get_namespaces"):
            return get_namespace(username, password)
        elif (function == "set"):
            return set(username, password, args[0], args[1], args[2], args[3])
        elif (function == "unset"):
            return unset(username, password, args[0], args[1], args[2], args[3])
        else:
            return "What happened?"


cpg.root = Server()
cpg.server.start(configFile="lnss-server.conf")
