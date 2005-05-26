#!/usr/bin/env python
"""Jonathan Roes' Local Names store.

Undocumented, so far.

Requires CherryPy.


= 2005-05-25 Lion =

NOTE!
* General interface test suite would be nice.

Work to do:
* (./) PEP-8-ify (- documentation)
* understand .conf files,
** if ok, make configuration variables into command-line arguments
** otherwise, do whatever you're supposed to by .conf file system
* guarantee working on taoriver
* update error codes
* use logging module instead of _log
* whatever decorators come with CherryPy
* PEP-8-ify (+ documentation)
* run & test (debug server)
* are all the functions present and accounted for?
** it seems that some aren't exposed
"""

import time
import os
import sys

import socket
import pprint
import cPickle as pickle
from cherrypy import cpg
import cherrypy.lib.filter.xmlrpcfilter


PATH_PREFIX = "/home/jroes/lnss/"
PATH_TO_CHERRYPY = PATH_PREFIX + "cherrypy" # this variable isn't used
MAIL = "/usr/sbin/sendmail"
HOST_NAME = "localnames.sosdg.org"
PORT_NUMBER = 9001
USERS_DB = PATH_PREFIX + "users.p"
WEB_DIR = "/home/jroes/public_html/"
URL_PREFIX = "http://localnames.sosdg.org/"


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

    """Local Names Store server.

    TODO: describe functions here
    """

    _cpFilterList = [cherrypy.lib.filter.xmlrpcfilter.XmlRpcFilter()]
    
    def _log(self, logstring):
        """Log an operation to the screen/logfile."""
        print time.asctime(), logstring
        return True

    def _opendb(s):
        """Open database."""
        try:
            self.userlist = pickle.load(open(USERS_DB, 'r'))
        except:
            self._log("--- User database doesn't exist, " +
                   "creating a new one.")
            self.userlist = {}
        self._log('--- Opened database: %s' % (USERS_DB,))
        return True
    
    def _savedb(self):
        """Save database."""
        pickle.dump(self.userlist, open(USERS_DB, 'w'))
        self._log('--- Saved database: %s' % (USERS_DB,))
        return True

    def _save_namespace(self, username, namespace_name):
        """Create a LocalNames description and pop it into a file."""
        f = open(WEB_DIR + username + "-" + namespace_name, 'w')
        f.write("X VERSION 1.1\n")
        for entry in self.userlist[username][namespace_name]:
            f.write(entry[0] + " \"" + entry[1] + "\" \"" + entry[2] +
                    "\"\n")

        f.close()

    def get_namespace(self, username, namespace):
        """Retrieve user's namespace file."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif not self.userlist[username].has_key(namespace):
            return NamespaceDoesntExistError
        elif namespace == "_password" or namespace == "_email":
            return AccessDeniedError
        else:
            return open(WEB_DIR + username + "-" + namespace_name,
                        'w').read()

    def __init__(self):
        self._opendb()

    def _cpOnError(self):
        import traceback, StringIO
        bodyFile = StringIO.StringIO()
        traceback.print_exc(file = bodyFile)
        errorBody = bodyFile.getvalue()        
        if cpg.request.isRPC: # Set by filter on XML-RPC requests
            # Convert traceback to dumped Fault object:
            # the XML-RPC exception
            import xmlrpclib
            result = xmlrpclib.dumps(xmlrpclib.Fault(1, errorBody))
            cpg.response.body = [result]
        else:
            ## handle regular web errors
            cpg.response.body = ['<pre>%s</pre>' % errorBody]

    def create_user(self, username, email, pw):
        """Create new user."""
        if self.userlist.has_key(username):
            return UserAlreadyExistsError
        else:
            self.userlist[username] = {}
            self.userlist[username]['_password'] = pw
            self.userlist[username]['_email'] = email

        self._log('New user: "%s"' % username)
        self._savedb()
        return True
    create_user.exposed = True

    def delete_user(self, username, pw):
        """Delete user."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            del self.userlist[username]

        self._log('Deleted user: "%s"' % username)
        self._savedb()
        return True
    delete_user.exposed = True

    def email_pw(self, username, email):
            """Email user's password to them."""
            if not self.userlist.has_key(username):
                return UserDoesntExistError
            else:
                message = ("To: " + email + "\n" +
                           "From: localnames\n" +
                           "Subject: password for localnames "
                           + HOST_NAME + ":" + str(PORT_NUMBER)
                           + "\n\n" +
                           "Your password is "
                           + self.userlist[username]['password'] + "\n")
                p = os.popen("%s -t" % MAIL, 'w')
                p.write(message)
                exitcode = p.close()
                return True
    email_pw.exposed = True

    def change_password(self, username, old_pw, new_pw):
        """Change user's password."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != old_pw:
            return IncorrectPasswordError
        else:
            self.userlist[username]['_password'] = new_pw
            self._savedb()
            return True

    def create_namespace(self, username, pw, namespace_name):
        """Create namespace."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif self.userlist[username].has_key(namespace_name):
            return NamespaceExistsError
        else:
            self.userlist[username][namespace_name] = [ ]
            return True

    def delete_namespace(self, username, pw, namespace_name):
        """Delete namespace."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == "_password":
            return AccessDeniedError
        elif self.userlist[username].has_key(namespace_name):
            del self.userlist[username][namespace_name]
            self._savedb()
            return True
        else:
            return NamespaceDoesntExistError

    def set(self, username, pw, namespace_name, entry_type, key, value):
        """Bind name to URL."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == '_password':
            return AccessDeniedError
        elif self.userlist[username].has_key(namespace_name):
            self.userlist[username][namespace_name].append(
                (entry_type, key, value))
            f = open(WEB_DIR + username + "-" + namespace_name, 'w')
            f.write("X VERSION 1.1\n")
            for entry in self.userlist[username][namespace_name]:
                f.write(entry[0] + " \"" + entry[1] + "\" \"" + entry[2]
                        + "\"\n")
            f.close()
            self._savedb()
            return True
        else:
            return NamespaceDoesntExistError

    def unset(self, username, pw, namespace_name, entry_type,
              key, value):
        """Unset namespace entry."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == '_password':
            return AccessDeniedError
        elif self.userlist[username].has_key(namespace_name):
            try:
                self.userlist[username][namespace_name].remove(
                    (entry_type, key, value))
                f = open(WEB_DIR + username + "-" + namespace_name, 'w')
                f.write("X VERSION 1.1\n")
                for entry in self.userlist[username][namespace_name]:
                    f.write(entry[0] + " \"" + entry[1] + "\" \"" +
                            entry[2] + "\"\n")
                f.close()
                self._savedb()
                return True
            except:
                return EntryDoesntExistError
        else:
            return NamespaceDoesntExistError

    def get_namespaces(self, username, pw):
        """Return list of namespaces."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            namespace_list = ""
            for user in self.userlist.keys():
                for namespace in self.userlist[user].keys():
                    if not namespace.startswith("_"):
                        namespace_list = (namespace_list + namespace +
                                          '\n')
            return namespace_list

    def get_server_info(self, username, pw):
        """Return information about the server."""
        return {'INTERFACE': 'v1 Local Names Store Interface',
                'IMPLEMENTATION': 'JROES-LNS-D3-V1',
                'SUPPORTS_PRIVATE_NAMESPACES': 0,
                'URL_NAME_PATTERN': ''}

    def get_namespace_url(self, username, pw, namespace_name):
        """Retrieve user's namespace."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == '_password':
            return AccessDeniedError
        elif self.userlist[username].has_key(namespace_name):
            return URL_PREFIX + username + "-" + namespace_name
        else:
            return NamespaceDoesntExistError

    def default(self, username, function, password, *args):
        if (function == "get_server_info"):
            return self.get_server_info(username, password)
        elif (function == "change_password"):
            return self.change_password(username, password, args[0])
        elif (function == "create_namespace"):
            return self.create_namespace(username, password, args[0])
        elif (function == "delete_namespace"):
            return self.delete_namespace(username, password, args[0])
        elif (function == "get_namespace_url"):
            return self.get_namespace_url(username, password, args[0])
        elif (function == "get_namespaces"):
            return self.get_namespaces(username, password)
        elif (function == "set"):
            return self.set(username, password,
                            args[0], args[1], args[2], args[3])
        elif (function == "unset"):
            return self.unset(username, password,
                              args[0], args[1], args[2], args[3])
        else:
            return "What happened?"
    default.exposed = True


if __name__ == "__main__":
    cpg.root = Server()
    cpg.server.start(configFile="lnss-server.conf")

