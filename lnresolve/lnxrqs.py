"""Local Names XML-RPC Query Server

You must put xrserve.py or xrcgi.py in the same directory as this module
in order to run the server or use this as a CGI.

DOC

DOC
"""

import lncore


XMLRPC_namespace = "lnquery"

"""Indicates to xrserve.py or xrcgi.py to publish this module.

Don't change this variable.

When xrserve.py (or xrcgi.py) run, they look for modules in the same
directory that define XMLRPC_namespace. It reads them, and then makes
their functions available by XML-RPC, over the web.
"""

store = lncore.Store()


def lookup(ns_url, name):
    """Lookup a single name within the named namespace.

    Use the Traditional lookup style.
    """
    resolver = lncore.Traditional(store)
    return resolver.find(ns_url, [name], lncore.LN)


def find(ns_url, find_path, record_type, style_name):
    """Lookup an entry.

    DOC
    """
    if style_name not in lncore.styles:
        return (-301, "unsupported style: %s")
    resolver = lncore.styles[style_name](store)
    return resolver.find(ns_url, find_path, record_type)


def find_many(ns_url, paths, record_type, style_name):
    """Lookup several entries.

    DOC
    """
    results = []
    for find_path in paths:
        results.append(find(ns_url, find_path, record_type, style_name))
    return results


def get_server_info():
    """Return a description of the query server implementation.

    DOC
    """
    result = {"INTERFACE": "v1 Local Names Query Interface",
              "IMPLEMENTATION": "OBS-LNQS",
              "CACHE": store.get_cache_list(),
              "STYLES": [style.info for style in lncore.styles],}
    return result


def get_cached_text(ns_url):
    """Return the text of the namespace description, as cached.

    For additional cache information, call lnquery.get_server_info.
    """
    result = store.get_cached_text(ns_url)
    if result == None:
        return (-302, "not cached")
    return (0, "ok")


def dump_cache(ns_url):
    """

    DOC
    """
    dumped = store.dump_cache(ns_url)
    if dumped == False:
        return (-302, "not cached")
    return (0, "ok")

