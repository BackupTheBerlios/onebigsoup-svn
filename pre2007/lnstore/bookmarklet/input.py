#!/usr/bin/env python2.4
"""Local Names Store Bookmarklet Data Entry Page

Render a data entry page. The page collects information that will be
stored in a Local Names namespace description by way of a Local Names
XML-RPC Store Interface. Values can be pre-filled, if they are GET
submitted as part of the request for this page.

Collect the following information (in the following named form fields):
* interface - URL of the LNXRStoreI
* password - password used when writing via the LNXRStoreI
* namespace - name of namespace to bind a local name in
* localname - local name to bind
* url - URL that local name will bind to
"""

import re

import shared


dollar_name = re.compile("\\$([a-z]+)")


if __name__ == "__main__":
    data = shared.read_cgi()
    def replace(match_object):
        name = match_object.groups()[0]
        if data.has_key(name):
            return data[name]
        elif shared.defaults.has_key(name):
            return shared.defaults[name]
        else:
            return ""
    template = open("input.html", "r").read()
    (result,
     num_replacements) = dollar_name.subn(replace,
                                          template)
    shared.start_page()
    print result.decode().encode("utf-8")

