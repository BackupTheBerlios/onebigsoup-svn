#!/usr/bin/env python2.4
"""Local Names Store Storage Action

Bind a local name in a namespace. You can use this from anywhere that
submits form data, by either GET or POST.

The following form fields must be defined:
* interface - URL of the LNXRStoreI
* password - password used when writing via the LNXRStoreI
* namespace - name of namespace to bind a local name in
* localname - local name to bind
* url - URL that local name will bind to

It returns the error string. That's "OK," when it works.
"""

import sys

import xmlrpclib

import shared


if __name__ == "__main__":
    data = shared.read_cgi()
    shared.start_page()
    for x in shared.form_keys:
        if x not in data:
            print u"missing definition for <b>%s</b>" % x
            sys.exit()
    server = xmlrpclib.ServerProxy(data["interface"])
    response = server.lnstore.set(data["password"], data["namespace"],
                                  "LN", data["localname"], data["url"])
    (err_code, err_string) = response
    print err_string

