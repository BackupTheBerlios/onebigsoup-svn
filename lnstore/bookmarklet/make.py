#!/usr/bin/env python2.4
"""Local Names Store Bookmarklet Maker

Create a Local Names Store Bookmarklet for the user.

The bookmarklet is made to work with the Local Names Store Bookmarklet
Data Entry Page, filling in whatever details it can.

The bookmarklet collects details based on the following form data:
* interface - URL of the LNXRStoreI
* password - password used when writing via the LNXRStoreI
* namespace - name of namespace to bind a local name in
* localname - local name to bind
* url - URL that local name will bind to
"""

import urllib

import shared


if __name__ == "__main__":
    data = shared.read_cgi()
    url = shared.INPUT_URL + "?" + urllib.urlencode(data)
    trick = ("javascript:" +
             "o=location.href;" +
             "location.href='" + url +
             "&url='+escape(o)")
    shared.start_page()
    print '<p>Here&apos;s your bookmarklet!</p>'
    print '<p><a href="%s">Store Local Name</a></p>' % trick
    print '<p>Drag it on up to wherever your bookmarks go,'
    print '   and you&apos;re set!</p>'
    print

