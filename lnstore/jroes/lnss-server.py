#!/usr/bin/env python
"""Jonathan Roes' Local Names store.

NOTE!
* General interface test suite would be nice.

Work to do:
* (./) PEP-8-ify (- documentation)
* (./) understand .conf files,
** if ok, make configuration variables into command-line arguments
** otherwise, do whatever you're supposed to by .conf file system
* guarantee working on taoriver
* (./) update error codes
* (./) use logging module instead of _log
* whatever decorators come with CherryPy
* PEP-8-ify (+ documentation)
* run & test (debug server)
"""

import time
import os
import sys

import socket
import pprint
import cPickle as pickle
from cherrypy import cpg
import cherrypy.lib.filter.xmlrpcfilter

import ConfigParser 
import logging

UserDoesntExistError = (-4, "User Doesn't Exist")
NamespaceDoesntExistError = (-100, "Namespace Doesn't Exist")
AccessDeniedError = (-1, "Permission Denied")
UserAlreadyExistsError = (-4, "User Already Exists")
IncorrectPasswordError = (-4, "Incorrect Password")
NamespaceExistsError = (-101, "Namespace Already Exists")
RecordNotFoundError = (-201, "Record Not Found")
InternalServerError = (-3, "Internal Server Error")

class Server:

    """Local Names Store server."""

    _cpFilterList = [cherrypy.lib.filter.xmlrpcfilter.XmlRpcFilter()]
    
    def _opendb(self):
        """Open database."""
        try:
            self.userlist = pickle.load(open(databasefile, 'r'))
        except:
            logger.info("User database doesn't exist, " +
                   "creating a new one.")
            self.userlist = {}
        logger.info('Opened database: %s' % (databasefile,))
        return True
    
    def _savedb(self):
        """Save database."""
        pickle.dump(self.userlist, open(databasefile, 'w'))
        logger.info('Saved database: %s' % (databasefile,))
        return True

    def _save_namespace(self, username, namespace_name):
        """Create a LocalNames description and pop it into a file."""
        f = open(webpath + username + "-" + namespace_name, 'w')
        f.write("X VERSION 1.1\n")
        for record in self.userlist[username][namespace_name]:
            f.write(record[0] + " \"" + record[1] + "\" \"" + record[2] +
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
            return open(webpath + username + "-" + namespace_name,
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

        logger.info('New user: "%s"' % username)
        self._savedb()
        return (0, "OK")
    create_user.exposed = True

    def delete_user(self, username, pw):
        """Delete user."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            del self.userlist[username]

        logger.info('Deleted user: "%s"' % username)
        self._savedb()
        return (0, "OK") 
    delete_user.exposed = True

    def email_pw(self, username, email):
            """Email user's password to them."""
            if not self.userlist.has_key(username):
                return UserDoesntExistError
            else:
                message = ("To: " + email + "\n" +
                           "From: localnames@localnames.sosdg.org\n" +
                           "Subject: password for localnames "
                           + hostname + ":" + str(PORT_NUMBER)
                           + "\n\n" +
                           "Your password is "
                           + self.userlist[username]['password'] + "\n")
                p = os.popen("%s -t" % MAIL, 'w')
                p.write(message)
                exitcode = p.close()
                return (0, "OK")
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
            return (0, "OK")

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
            self._save_namespace(username, namespace_name)
            return (0, "OK")

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
            return (0, "OK")
        else:
            return NamespaceDoesntExistError

    def set(self, username, pw, namespace_name, record_type, key, value):
        """Bind name to URL."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        elif namespace_name == '_password':
            return AccessDeniedError
        elif record_type not in ["LN", "X", "NS", "PATTERN"]:
            return BadRecordTypeError
        elif self.userlist[username].has_key(namespace_name):
            self.userlist[username][namespace_name].append(
                (record_type, key, value))
            f = open(webpath + username + "-" + namespace_name, 'w')
            f.write("X VERSION 1.1\n")
            for entry in self.userlist[username][namespace_name]:
                f.write(entry[0] + " \"" + entry[1] + "\" \"" + entry[2]
                        + "\"\n")
            f.close()
            self._savedb()
            return (0, "OK")
        else:
            return NamespaceDoesntExistError

    def unset(self, username, pw, namespace_name, record_type,
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
                    (record_type, key, value))
                f = open(webpath + username + "-" + namespace_name, 'w')
                f.write("X VERSION 1.1\n")
                for entry in self.userlist[username][namespace_name]:
                    f.write(entry[0] + " \"" + entry[1] + "\" \"" +
                            entry[2] + "\"\n")
                f.close()
                self._savedb()
                return (0, "OK")
            except:
                return RecordNotFoundError
        else:
            return NamespaceDoesntExistError

    def get_namespaces(self, username, pw):
        """Return list of namespaces."""
        if not self.userlist.has_key(username):
            return UserDoesntExistError
        elif self.userlist[username]['_password'] != pw:
            return IncorrectPasswordError
        else:
            namespace_list = []
            for namespace in self.userlist[username].keys():
                if not namespace.startswith("_"):
                    namespace_list.append(namespace)
            return namespace_list

    def get_server_info(self, username, pw):
        """Return information about the server."""
        return {'INTERFACE': 'v1 Local Names Store Interface',
                'IMPLEMENTATION': 'JROES-LNS-D3-V1',
                'SUPPORTS_PRIVATE_NAMESPACES': 0,
                'SERVER_NAMESPACE_URL': '',
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
            return url + username + "-" + namespace_name
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
            return InternalServerError
    default.exposed = True


if __name__ == "__main__":
        config = ConfigParser.ConfigParser()
        config.read("lnss-server.conf")
        databasefile = config.get("paths", "databasefile")
        sendmailpath = config.get("paths", "sendmailpath")
        url = config.get("paths", "url")
        webpath = config.get("paths", "webpath")

        logger = logging.getLogger('lnss')
        hdlr = logging.FileHandler('lnss.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)
        
        cpg.root = Server()
        cpg.server.start(configFile="lnss-server.conf")
