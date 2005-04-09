#!/usr/bin/env python

import time, socket, pprint, xmlrpclib, os, sys
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
AccessDenied = -3
UserAlreadyExistsError = -4
IncorrectPasswordError = -5
NamespaceExistsError = -6


"""
complies with V3 of the LNSS Interface Specification:
http://onebigsoup.wiki.taoriver.net/moin.cgi/LocalNamesStoreXmlRpcInterface

references:
http://www.cherrypy.org/wiki/XmlRpcFilter
http://www.cherrypy.org/wiki/CherryPyTutorial

userlist structure:
dictionary {
 key: email
 value: dictionary { 
 key is going to be the namespace name
 disallow any namespace called 'password', as we store the password there...
 also, don't let anyone read that key except us
 key: 'password' value: password
 key: -namespace_name   dictionary {
 --entry_type
 --key
 --value }
}

"""


class Server:
#	_cpFilterList = [xmlrpcfilter.XmlRpcFilter()] 

	def _log(s, logstring):
		"""
		Logs an operation to the screen/logfile
		"""
		print time.asctime(), logstring
		return True
	
	def _opendb(s):
		"""
		Opens database.
		"""
		try:
			s.userlist = pickle.load( open(USERS_DB, 'r') )
		except:
			s._log("--- User database doesn't exist.  New database started.")
			s.userlist = { }
		s._log('--- Opened database: %s' % (USERS_DB,))
		
		return True

	def _savedb(s):
		"""
		Saves database.
		"""
		pickle.dump( s.userlist, open(USERS_DB, 'w') )
		s._log('--- Saved database: %s' % (USERS_DB,))
		return True
	
	def _save_namespace(s, email, namespace_name):
		"""
		Create a LocalNames description and pop it into a file
		"""
		f = open(WEB_DIR + email + "-" + namespace_name, 'w')
		f.write("X VERSION 1.1\n")
		for entry in s.userlist[email][namespace_name]:
			f.write(entry[0] + " \"" + entry[1]  + "\" \"" + entry[2] + "\"\n")
				
		f.close()

	def get_namespace(s, email, namespace):
		"""
		Retrieves user's namespace file

		email:		email address of user (string)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif not s.userlist[email].has_key(namespace):
			return NamespaceDoesntExistError
		elif namespace == "password":
			return AccessDenied
		else:
			return open(WEB_DIR + email + '-' + namespace_name, 'w').read()
		
	def __init__( s ):
		s._opendb()

	def create_user(s, email, pw):
		"""
		Creates a new user.

		email:		email address of user (string)
		password:	password for user (string)
		"""
		if s.userlist.has_key(email):
			return UserAlreadyExistsError
		else:
			s.userlist[email] = { }
			s.userlist[email]['password'] = pw 
		s._log('New user: "%s"' % email)
		s._savedb()
		return True
	
	def delete_user(s, email, pw):
		""" 
		Deletes user.
		
		email:		email address of user (string)
		password:	password of user (string)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != pw:
			return IncorrectPasswordError
		else:
			del s.userlist[email]

		s._log('Deleted user: "%s"' % email)
		s._savedb()
		return True

	def email_pw(s, email):
		"""
		Emails user their password.

		email:		email address of user (string)
		"""
		if not s.userlist.has_key(email):
			return False
		else:
			message =  "To: " + email + "\n"
			message += "From: localnames\n"
			message += "Subject: password for localnames " + HOST_NAME + ":" + str(PORT_NUMBER) + "\n\n"
			message += "Your password is " + s.userlist[email]['password'] + "\n"
			p = os.popen("%s -t" % MAIL, 'w')
			p.write(message)
			exitcode = p.close()
			return True

# -------------------------------
# Interface implementation
# -------------------------------
	def change_password(s, email, old_pw, new_pw):
		"""
		Changes user's password.

		email:		email address of user (string)
		old_pw:		old password (string)
		new_pw:		new password (string)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != old_pw:
			return IncorrectPasswordError
		else:
			s.userlist[email]['password'] = new_pw
			s._savedb()
			return True

	def create_namespace(s, email, pw, namespace_name):
		"""
		Creates a namespace

		email:		email address of user (string)
		pw:		password of user (string)
		namespace_name: name of namespace to create (string)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != pw:
			return IncorrectPasswordError
		elif s.userlist[email].has_key(namespace_name):
			return NamespaceExistsError
		elif namespace_name == "password":
			return AccessDeniedError
		else:
			s.userlist[email][namespace_name] = [ ]
			return True

	def delete_namespace(s, email, pw, namespace_name):
		"""
		Deletes a namespace
		
		email:		email address of user (string)
		pw:		password of user (string)
		namespace_name: name of namespace to delete (string)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != pw:
			return IncorrectPasswordError
		elif namespace_name == "password":
			return AccessDeniedError
		elif s.userlist[email].has_key(namespace_name):
			del s.userlist[email][namespace_name]
			s._savedb()
			return True
		else:
			return NamespaceDoesntExistError

	def set(s, email, pw, namespace_name, entry_type, key, value):
		"""
		Binds name to URL
		
		email:		email address of user (string)
		pw:		password of user (string)
		namespace_name: name of namespace to set entry in (string)
		entry_type:	type of entry (NS, X, LN, PATTERN)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != pw:
			return IncorrectPasswordError
		elif namespace_name == "password":
			return AccessDeniedError
		elif s.userlist[email].has_key(namespace_name):
			s.userlist[email][namespace_name].append( (entry_type, key, value) )	
			f = open(WEB_DIR + email + "-" + namespace_name, 'w')
			f.write("X VERSION 1.1\n")
			for entry in s.userlist[email][namespace_name]:
				f.write(entry[0] + " \"" + entry[1]  + "\" \"" + entry[2] + "\"\n")
			f.close()
			s._savedb()
			return True
		else:
			return NamespaceDoesntExistError
			
	def unset(s, email, pw, namespace_name, entry_type, key, value):
		"""
		Unsets key, value, entry_type in namespace_name
		
		email:		email address of user (string)
		pw:		password of user (string)
		namespace_name: name of namespace to unset the entry in
		entry_type:	type of entry (NS, X, LN, PATTERN)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != pw:
			return IncorrectPasswordError
		elif namespace_name == "password":
			return AccessDeniedError
		elif s.userlist[email].has_key(namespace_name):
			try:
				s.userlist[email][namespace_name].remove( (entry_type, key, value) )
				f = open(WEB_DIR + email + "-" + namespace_name, 'w')
				f.write("X VERSION 1.1\n")
				for entry in s.userlist[email][namespace_name]:
					f.write(entry[0] + " \"" + entry[1]  + "\" \"" + entry[2] + "\"\n")
				f.close()
				s._savedb()
				return True
			except:
				return EntryDoesntExistError
		else:
			return NamespaceDoesntExistError

	def get_namespaces(s, username, pw):
		"""
		Returns list of namespaces

		username:	username of user (string)
		pw:		password of user (string)
		"""
		if not s.userlist.has_key(username):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != pw:
			return IncorrectPasswordError
		else:
			namespace_list = ""
			for user in s.userlist:
				for namespace in user:
					namespace_list = namespacelist + namespace + "\n"
			return namespace_list

	def get_server_info(s, username, pw):
		"""
		Returns information about server

		username:	username of user (string)
		pw:		password of user (string)
		"""
		return { 'INTERFACE': 'v1 Local Names Store Interface', 'IMPLEMENTATION': 'JROES-LNS-D3-V1', 'SUPPORTS_PRIVATE_NAMESPACES': 0, 'URL_NAME_PATTERN': '' }

	def get_namespace_url(s, email, pw, namespace_name):
		"""
		Gets namespace url

		email:		email address of user (string)
		pw:		password of user (string)
		namespace_name: name of namespace (string)
		"""
		if not s.userlist.has_key(email):
			return UserDoesntExistError
		elif s.userlist[email]['password'] != pw:
			return IncorrectPasswordError
		elif namespace_name == "password":
			return AccessDeniedError
		elif s.userlist[email].has_key(namespace_name):
			return URL_PREFIX + email + "-" + namespace_name
		else:
			return NamespaceDoesntExistError

	def default(s, username, function, password, *args):
		default.exposed = True

		if not s.userlist.has_key(username):
			return UserDoesntExistError
#		I want to do this but I know it won't work, we'll rehash it to something similar later:
#		else:
#			return function(*args)
#		"""
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
