#!/usr/bin/env python
"""Serve specially marked modules by XML-RPC.

  -Hhostname   host name, default ""
  -Pportnum    port number, default 8000

This script starts an XML-RPC server, and publishes auto-detected
modules from the working directory.

Functions within Modules that define the name "XMLRPC_namespace" are
published. Function names that begin with an underscore (ex: _eggs) are
not published. Functions are published within the XML-RPC namespace
designated by the XMLRPC_namespace value, or the base namespace if the
value is None.
"""

import time
import os
import sets
import imp
import types

import optparse
import DocXMLRPCServer


def find_modules(path="."):
    """Return names of modules in a directory.

    Returns module names in a list. Filenames that end in ".py" or
    ".pyc" are considered to be modules. The extension is not included
    in the returned list.
    """
    modules = sets.Set()
    for filename in os.listdir(path):
        module = None
        if filename.endswith(".py"):
            module = filename[:-3]
        elif filename.endswith(".pyc"):
            module = filename[:-4]
        if module is not None:
            modules.add(module)
    return list(modules)


def load_module(name, path=["."]):
    """Return a named module found in a given path."""
    (file, pathname, description) = imp.find_module(name, path)
    return imp.load_module(name, file, pathname, description)


def find_xmlrpc_modules():
    """Find modules that define XMLRPC_namespace.

    Loads all modules in the current working directory. Returns a list
    of modules, the modules that define XMLRPC_namespace.
    """
    modules = [load_module(m) for m in find_modules()]
    xmlrpc_modules = []
    for m in modules:
        if m.__dict__.has_key("XMLRPC_namespace"):
            xmlrpc_modules.append(m)
    return xmlrpc_modules


def functions_in_module(module):
    """Find all functions in a module."""
    functions = []
    for obj in module.__dict__.values():
        if isinstance(obj, types.FunctionType):
            functions.append(obj)
    return functions


if __name__ == "__main__":
    parser = optparse.OptionParser(__doc__)
    parser.add_option("-H", "--host", dest="hostname",
                      default="127.0.0.1", type="string",
                      help="specify hostname to run on")
    parser.add_option("-p", "--port", dest="portnum", default=8000,
                      type="int", help="port number to run on")

    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    ServerClass = DocXMLRPCServer.DocXMLRPCServer
    server = ServerClass((options.hostname, options.portnum),
                         logRequests=0)

    for module in find_xmlrpc_modules():
        for func in functions_in_module(module):
            if func.__name__.startswith("_"):
                continue
            full_name = func.__name__
            if module.XMLRPC_namespace is not None:
                full_name = "%s.%s" % (module.XMLRPC_namespace,
                                       full_name)
            server.register_function(func, full_name)

    server.set_server_title("xrserver")
    server.register_introspection_functions()

    print time.asctime(), 'Application Starting.'
    server.serve_forever()
    print time.asctime(), 'Application Finishing.'
