#!/usr/bin/env python
# DeliciousNames: create a LocalNames namespace from your del.icio.us
# bookmarks
# To use: edit 'username' and 'password' strings, and run as a script.
import xml.parsers.expat, urllib2

authinfo = urllib2.HTTPBasicAuthHandler()
authinfo.add_password('del.icio.us API', 'http://del.icio.us', 'username', 'password')
urllib2.install_opener(urllib2.build_opener(authinfo))

posts = []
def hst(name, attrs):
    if name == "post": posts.append(attrs.get('href', ''), attrs.get('extended', '')

p = xml.parsers.expat.ParserCreate()
p.StartElementHandler = hst
p.Parse(urllib2.urlopen("http://del.icio.us/api/posts/all").read())

print "X VERSION 1.1"
for post in posts: if post[1] != '': print 'LN "%s" "%s"' % (post[1], post[0])
