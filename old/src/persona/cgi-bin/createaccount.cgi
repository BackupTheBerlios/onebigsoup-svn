#!/usr/bin/env python
import cgi
import xmlrpclib
import sha

form = cgi.FieldStorage()

print "Content-type: text/html\n\n"

if form.has_key('submit'): # submitting form
   userinfo = { 'firstname' : form["firstname"].value, 
	       'lastname' : form["lastname"].value, 
	       'email' : form["email"].value, 
	       'homepage' : form["homepage"].value, 
	       'picture' : form["picture"].value,
               'password' : sha.new(form["password"].value).hexdigest()
   }

   ps = xmlrpclib.ServerProxy(form['server_address'].value)
   # TODO: Find out just how safe my password scheme is.
   # (Probably not very/at all)
   try:
      ps.newuser(form["userid"].value, userinfo)
      print open('success_created.html', 'r').read()
   except UserAlreadyExistsError:
      print open('error_exists.html', 'r').read()
      
else:
   print open('create_form.html', 'r').read()

