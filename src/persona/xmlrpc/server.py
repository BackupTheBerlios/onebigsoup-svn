#!/usr/bin/env python

import time
import socket
import pprint
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
import cPickle as pickle
import sha

import Foaf

HOST_NAME = "everest.2mbit.com"
PORT_NUMBER = 9500 
DB_FILE = "/home/jroes/dev/personalserver/xmlrpc/userdb.p"

"""
 userlist - dictionary of userinfos - indexed by userid
 userinfo structure:
  * password md5 / sha / pgp key?
  * firstname
  * lastname
  * email
  * homepage
  * picture
  * plog_uri
  * publickey

 Functions you can call:

 <id> newuser(userid, password, userinfo): creates new user
 <success> verifyuser(userid, password): verifies user is owner of userid
 <success> deluser(userid, password): deletes specified user
 <success> edituser(userid, password, newuserinfo): changes user details
 <foaf> getfoaf(userid): retrieves FOAF based on user's personal info
 <ploguri> getplog(userid): retrieves plog URI for user
 notify(source, channel): receives notify from event server

 TODO: separate user functions into user.py
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
		Saves user database.
		"""
		pickle.dump( s.userlist, open(DB_FILE, 'w') )
		s._log('--- Saved user database: %s' % (DB_FILE,))
		return True

	def _opendb(s):
		"""
		Opens user database.
		"""
		try:
			s.userlist = pickle.load( open(DB_FILE, 'r') )
			s._log('--- Opened database: %s' % (DB_FILE))
		except IOError:
			s._log("--- Database doesn't exist.  New database started.")
			s.userlist = { }
			
		return True
	
	def __init__( s, host_name, port_number ):
		s.host_name = host_name
		s.port_number = port_number
		s._opendb()

	def newuser(s, userid, userinfo):
		"""
		Creates a new user.

		userid:		userid of user (string)
		userinfo:	user information (dictionary)
		"""
		if s.userlist.has_key(userid):
			return UserAlreadyExistsError
		else:
			s.userlist[userid] = userinfo
		s._log('New user: "%s"' % userid)
		s._savedb()
		return True
	
	def edituser(s, userid, password, newuserinfo):
		"""
		Changes a users details.

		userid:		userid of user (string)
		password:	password of user (encrypted string)
		newuserinfo:	user information (dictionary)
		"""
		if s.userlist.has_key(userid) == None:
			return UserDoesntExistError
		elif s.userlist[userid]['password'] != password:
			return IncorrectPasswordError
		else:
			s.userlist[userid] = newuserinfo

		s._savedb()
		return True


	def deluser(s, userid, password):
		""" 
		Deletes user.
		
		userid:		userid of user (string)
		password:	password of user (encrypted string)
		"""
		if s.userlist[userid] == None:
			return UserDoesntExistError
		elif s.userlist[userid]['password'] != password:
			return IncorrectPasswordError
		else:
			del s.userlist[userid]

		s._log('Deleted user: "%s"' % userid)
		s._savedb()
		return True

	def verifyuser(s, userid, password):
		"""
		Verifies user.  (ensures this the right person)

		userid:		userid of user (string)
		password:	password of user (encrypted string)
		"""

		if s.userlist[userid] == None:
			return UserDoesntExistError
		elif s.userlist[userid]['password'] != password:
			return IncorrectPasswordError
		else:
			return True

	def getfoaf(s, userid):
		"""
		Gets a generated FOAF for userid

		userid:		userid of user (string)
		"""
		if s.userlist[userid] == None:
			return UserDoesntExistError
		else:
			return Foaf.getfoaf(HOST_NAME + ':' + str(PORT_NUMBER), s.userlist[userid])

	def getplog(s, userid):
		""" 
		Retrieves plog URI for user.
		
		userid:		userid of user (string)
		"""
		if s.userlist[userid] == None:
			return UserDoesntExistError
		else:
			return s.userlist[userid]["plog_uri"]
    	

	def notify( s, channel, load ):
		print "Received:", time.asctime()
		print "Channel:", channel
		print pprint.pprint( load )
		print "------------------------------------------"
		return 1

	def run( s ):
		server = SimpleXMLRPCServer( (s.host_name, s.port_number),
					  logRequests=0 )
		server.register_function( s.notify )
		server.register_function( s.newuser )
		server.register_function( s.edituser )
		server.register_function( s.deluser )
		server.register_function( s.verifyuser )
		server.register_function( s.getfoaf )
		server.register_function( s.getplog )
		print time.asctime(), "Personal Server Starts - %s:%s" % (s.host_name,
									  s.port_number)
		try:
			server.serve_forever()
		except KeyboardInterrupt:
			pass
		print time.asctime(), "Personal Server Stops - %s:%s" % (s.host_name,
                                                             s.port_number)


if __name__ == "__main__":
    server = Server( HOST_NAME, PORT_NUMBER )
    server.run()
