#!/usr/bin/env python
"""Ad-hoc Local Names XML-RPC Query Server Cache Dump Utility

I made this real quick, just to get the functionality out the door.
"""

import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import xmlrpclib


LNXRQS="http://ln.taoriver.net/lnxrqs"  # URL of query server
ACTION="dumpcache"  # how the script is accessed


print "Content-type: text/html"
print

print """
<html>

<head><title>Local Names XML-RPC Server Cache Dump Utility</title></head>

<body>

  <h3> Local Names XML-RPC Server Cache Dump Utility </h3>
"""

form = cgi.FieldStorage()
ns_url = form.getvalue("ns_url", "(no ns_url)")

if ns_url != "(no ns_url)":
    s = xmlrpclib.ServerProxy(LNXRQS)
    result = str(s.lnquery.dump_cache(ns_url))
else:
    result = "(no result)"

print """

  <p>Received: %s</p>
  <p>Result: %s</p>

  <p>Utility to tell <a href="%s">%s</a> to dump a cached namespace description.</p>

  <form method="get" action="dumpcache">
    <p>namespace description URL (ns_url): <input type="text" name="ns_url"/></p>
  </form>

</body>

</html>
""" % (ns_url, result, LNXRQS, LNXRQS)

