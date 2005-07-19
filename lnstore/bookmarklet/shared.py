"""Shared Bookmarklet Code

This contains:
* configuration data for all scripts in this directory
* shared code, used by scripts in this directory

TODO
"""

import cgi


INPUT_URL = "http://taoriver.net/TODO/input.py"
"""URL for user input page.

Where the user is sent when they click on the bookmarklet.
"""

ACTION_URL = "http://taoriver.net/TODO/action.py"
"""URL for action page.

The last page the user visits; All information needed to bind a name to
a URL should be collected by the time this page is rendered.
"""

DEFAULT_LNXRSTOREI = "http://taoriver.net/TODO/xrcgi.py"
"""URL for default Local Names XML-RPC Store Interface.

This system can actually make use of any Local Names XML-RPC Store
Interface. But it's intented to be configured for one by default.
"""


defaults = {"namespace": "default",
            "interface": DEFAULT_LNXRSTOREI,
            "password": "password"}
"""Default values on the input page."""

form_keys = ["interface", "password", "namespace", "localname", "url"]
"""Keys used to process common form data."""


def read_cgi():
    """TODO"""
    received = cgi.parse()
    final_dictionary = {}
    for ok_key in form_keys:
        if received.has_key(ok_key):
            final_dictionary[ok_key] = received[ok_key][0]
    return final_dictionary

def start_page():
    """TODO"""
    print "Content-type: text/html; charset=utf-8"
    print

