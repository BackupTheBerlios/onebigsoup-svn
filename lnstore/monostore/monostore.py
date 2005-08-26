"""MonoStore: an Local Names XML-RPC Store Interface implementation.

The MonoStore is very simple: It maintains a single namespace
description. It's about as simple as an LNXRStoreI implementation can
get.

This module is made to be called via xrcgi.py, the code for which can be
found on the PythonInfo wiki:  http://wiki.python.org/moin/AutoXmlRpcCgi

BUG: You can only have ONE extension value per extension key! That is,
an X record can only have one value per key. By the Local Names
Namespace Description Specification version 1.2, you are supposed to be
able to have an unlimited number of extension values per extension
key. (TODO)

Configure this script to your web server and filesystem by editing the
marked variables at the top of the script.

NAMESPACE_DESCRIPTION_PATH  -- location of namespace description
NAMESPACE_DESCRIPTION_URL  -- how general public finds description
NAMESPACE_DATA_PATH  -- location of namespace data
get_server_info  -- returns info about server
change_password  -- does nothing
create_namespace  -- does nothing
delete_namespace  -- does nothing
get_namespaces  -- returns ["default"], always
get_namespace_url  -- returns NAMESPACE_DESCRIPTION_URL
set  -- set namespace values
unset  -- remove namespace values
"""

import re
import bsddb
import xmlrpclib


NAMESPACE_DESCRIPTION_PATH = "/var/www/html/ns.txt"  # Change this
"""Filesystem location of the namespace description.

Set this to where you want the script to store the namespace
description. Configure the filesystem and the web server so that the web
server user (perhaps "apache") has read and write access to the
namespace description.
"""

NAMESPACE_DESCRIPTION_URL = "http://example.net/ns.txt"  # Change this
"""URL of the namespace description.

Set this to the URL of the same namespace description. Configure the
filesystem and the web server so that the general public can read the
namespace description.
"""

NAMESPACE_DATA_PATH = "/var/www/data/monostore.bsddb"  # Change this
"""Filesystem location of the namespace data store.

The code uses a Berkeley Sleepycat Database (bsddb) to keep
state. Configure the filesystem and the web server so that the web
server user (perhaps "apache") has read and write access to this file.
"""


XMLRPC_namespace = "lnstore"  # Do not change

key_encoding_re = re.compile(r'([A-Z]+)\.(.+)')  # Do not change


def _escape_string(s):
    """Escape a string for presentation in a namespace description."""
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    return '"' + s + '"'


def _output_page():
    """Write the Local Names namespace description."""
    f = open(NAMESPACE_DESCRIPTION_PATH, "w")
    f.write("X VERSION 1.1\n")
    db = bsddb.hashopen(NAMESPACE_DATA_PATH)
    for key in db:
        value = db[key]
        match_object = key_encoding_re.match(key)
        (record_type, record_name) = match_object.groups()
        f.write("%s %s %s\n" % (record_type,
                                _escape_string(record_name),
                                _escape_string(value)))
    db.close()
    f.close()


def _dump_cache(query_server_url, ns_url):
    """Tell a query server to dump a namespace description."""
    if ns_url is None or query_server_url is None:
        return
    server = xmlrpclib.ServerProxy(query_server_url)
    try:
        server.lnquery.dump_cache(ns_url)
    except e:
        pass


def get_server_info(pw):
    """Return a description of the store interface implementation."""
    return {"INTERFACE": "v1 Local Names Store Interface",
            "IMPLEMENTATION": "LION-MONOSTORE-V1",
            "SUPPORTS_PRIVATE_NAMESPACES": 0,
            "SERVER_NAMESPACE_URL": "",
            "URL_NAME_PATTERN": NAMESPACE_DESCRIPTION_URL,
            "TITLE": "Lion's MonoStore Local Names Store Server",
            "DESCRIPTION": ("A Local Names Store Server that stores "
                            "just one, single, unpassword-protected "
                            "Local Names namespace description. It's "
                            "mainly used for development and testing "
                            "purposes."),
            "COMMENTS": ("Warning: this server can only store "
                         "one extension value per extension key.")}


def change_password(pw, new_pw):
    """This server doesn't feature passwords, so this does nothing."""
    return (-2, "not implemented")


def create_namespace(pw, name_of_namespace):
    """This server has only one namespace, so this does nothing."""
    return (-2, "not implemented")


def delete_namespace(pw, name_of_namespace):
    """This server always has only one namespace; this does nothing."""
    return (-2, "not implemented")


def get_namespaces(pw):
    """This server has only one namespace, this is always the same.

    Since the server only has one namespace, it always returns
    ["default"].
    """
    return ["default"]


def get_namespace_url(pw, name_of_namespace):
    """Returns the URL of the default namespace."""
    return NAMESPACE_DESCRIPTION_URL


def set(pw, name_of_namespace, record_type, name, value):
    """Set data within the namespace.

    This server has a limitation; It can only store ONE X record value
    per key.
    """
    if record_type not in ["LN", "NS", "PATTERN", "X"]:
        return (-200, "bad record type- valid: LN, NS, X, PATTERN")
    db = bsddb.hashopen(NAMESPACE_DATA_PATH)
    db[record_type + "." + name] = value
    query_server_url = db.get("X.PREFERRED-QUERY-SERVER")
    db.close()
    _output_page()
    _dump_cache(query_server_url, NAMESPACE_DESCRIPTION_URL)
    return (0, "OK")


def unset(pw, name_of_namespace, record_type, name, value):
    """Unset data within the namespace."""
    if record_type not in ["LN", "NS", "PATTERN", "X"]:
        return (-200, "bad record type- valid: LN, NS, X, PATTERN")
    db = bsddb.hashopen(NAMESPACE_DATA_PATH)
    if not db.has_key(record_type + "." + name):
        return (-201, "record not found")
    if db[record_type + "." + name] != value:
        return (-201, "record not found")
    del db[record_type + "." + name]
    query_server_url = db.get("X.PREFERRED-QUERY-SERVER")
    db.close()
    _output_page()
    _dump_cache(query_server_url, NAMESPACE_DESCRIPTION_URL)
    return (0, "OK")

