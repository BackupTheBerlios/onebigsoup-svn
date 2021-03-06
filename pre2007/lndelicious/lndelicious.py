#!/usr/bin/env python
"""Create a Local Names namespace from del.icio.us bookmarks.

The extended field is interpreted as the Local Name for the link.

The local names namespace description is output to stdout.
"""

import urllib2
import xml.parsers.expat

authinfo = urllib2.HTTPBasicAuthHandler()
authinfo.add_password('del.icio.us API', 'http://del.icio.us', raw_input("Username: "), raw_input("Password: "))
urllib2.install_opener(urllib2.build_opener(authinfo))

posts = []
def hst(n,a): (n == "post") and (posts.append((a.get('href',''),a.get('extended',''))))

parser = xml.parsers.expat.ParserCreate(); parser.StartElementHandler = hst
parser.Parse(urllib2.urlopen("http://del.icio.us/api/posts/all").read())

print "X VERSION 1.1"
for (n,u) in filter(lambda p: p[1]!="", posts): print 'LN "%s" "%s"' % (n,u)

