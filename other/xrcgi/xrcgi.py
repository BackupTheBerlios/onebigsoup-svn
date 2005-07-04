#!/usr/bin/env python2.4
"""CGI between XML-RPC web requests, and specially marked modules.

This script is a gateway (CGI) between web XML-RPC requests, and
Python modules that define "XMLRPC_namespace".

Functions within Modules that define the name "XMLRPC_namespace" are
accessible by XML-RPC. Function names that begin with an underscore (ex:
_eggs) are not published. Functions are published within the XML-RPC
namespace designated by the XMLRPC_namespace value, or the base
namespace if the value is None.
"""

import time
import os
import sets
import imp
import types

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
    handler = DocXMLRPCServer.DocCGIXMLRPCRequestHandler()
    
    for module in find_xmlrpc_modules():
        for func in functions_in_module(module):
            if func.__name__.startswith("_"):
                continue
            full_name = func.__name__
            if module.XMLRPC_namespace is not None:
                full_name = "%s.%s" % (module.XMLRPC_namespace,
                                       full_name)
            handler.register_function(func, full_name)
    
    handler.set_server_title("xrserver")
    handler.register_introspection_functions()
    handler.register_multicall_functions()
    handler.handle_request()

