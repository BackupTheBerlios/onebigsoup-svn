#!/usr/bin/env python
import cgi

form = cgi.FieldStorage()

if form.has_key('userid') and form.has_key('server_address'):
   ps = xmlrpclib.ServerProxy(form['server_address'].value)
   try:
      foaf = ps.getfoaf(userid)
   except:
      print "Content-Type: text/html\n\n"
      print open('notfound_error.html', 'r').read()
else:
   print "Content-Type: text/html\n\n"
   print "Unknown request.  Please specify a userid or server address."
