#!/usr/bin/env python

import time
import socket
import pprint
import xmlrpclib
from DocXMLRPCServer import DocXMLRPCServer
import cPickle as pickle
import os

MAIL = "/usr/sbin/sendmail"
HOST_NAME = "localnames.sosdg.org"
PORT_NUMBER = 9001
USERS_DB = "/home/jroes/lnss/users.p"
WEB_DIR = "/home/jroes/public_html/"
URL_PREFIX = "http://localnames.sosdg.org/"


UserDoesntExistError = -1
NamespaceDoesntExistError = -2
AccessDenied = -3
UserAlreadyExistsError = -4
IncorrectPasswordError = -5
NamespaceExistsError = -6


"""
LNSS Interface Specification:
http://onebigsoup.wiki.taoriver.net/moin.cgi/LocalNamesStoreXmlRpcInterface

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

 Functions you can call:

 Users:
 create_user(email, pw): creates new user
 delete_user(email, pw): deletes a user
 email_pw(email): emails password to user
 change_pw(email, old_pw, new_pw): changes user's password

 Namespaces:
 create_namespace(email, pw, namespace_name): creates a namespace
 delete_namespace(email, pw, namespace_name): deletes a namespace

 Edits:
 set(email, pw, namespace_name, entry_type, key, value): sets up a new entry in the namespace
 unset(email, pw, namespace_name, entry_type, key, value): unbinds entry in namespace
 get_description_url(email, pw, namespace_name): get URL of namespace

"""

class Server:
	def _log(s, logstring):
		"""
		Logs an operation to the screen/logfile
		"""
		print time.asctime(), logstring
		return True
	
	def _savedb(s):
		"""
		Saves database.
		"""
		pickle.dump( s.userlist, open(USERS_DB, 'w') )
		s._log('--- Saved database: %s' % (USERS_DB,))
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
	
	def save_namespace(s, email, namespace_name):
		"""
		Create a LocalNames description and pop it into a file
		"""
		f = open(WEB_DIR + email + "-" + namespace_name, 'w')
		f.write("X VERSION 1.1\n")
		for entry in s.userlist[email][namespace_name]:
			f.write(entry[0] + " " + entry[1]  + " " + entry[2] + "\n")
				
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
		
	def __init__( s, host_name, port_number ):
		s.host_name = host_name
		s.port_number = port_number
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

	def change_pw(s, email, old_pw, new_pw):
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
			#s.save_namespace(s, email, namespace_name)
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
					f.write(entry[0] + " " + entry[1]  + " " + entry[2] + "\n")
				f.close()
				#s.save_namespace(s, email, namespace_name)
				s._savedb()
				return True
			except:
				return EntryDoesntExistError
		else:
			return NamespaceDoesntExistError


	def get_description_url(s, email, pw, namespace_name):
		"""
		Gets description url

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

	def notify( s, channel, load ):
		print "Received:", time.asctime()
		print "Channel:", channel
		print pprint.pprint( load )
		print "------------------------------------------"
		return 1

	def run( s ):
		server = DocXMLRPCServer( (s.host_name, s.port_number),
					  logRequests=0 )
		server.register_function( s.notify )
		server.register_function( s.create_user )
		server.register_function( s.delete_user )
		server.register_function( s.email_pw )
		server.register_function( s.change_pw )
		server.register_function( s.create_namespace )
		server.register_function( s.delete_namespace )
		server.register_function( s.set )
		server.register_function( s.unset )
		server.register_function( s.get_description_url )
		server.register_introspection_functions()

		print time.asctime(), "Local Names Store Server Starts - %s:%s" % (s.host_name,
									  s.port_number)
		try:
			server.serve_forever()
		except KeyboardInterrupt:
			pass
		print time.asctime(), "Local Names Store Server Stops - %s:%s" % (s.host_name,
                                                             s.port_number)


if __name__ == "__main__":
    server = Server( HOST_NAME, PORT_NUMBER )
    server.run()
