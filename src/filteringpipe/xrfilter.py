#!/usr/bin/python2.3
"""
xrfilter.py -- output result of passing stdin through an XmlRpcFilteringPipe

"""

import sys
import optparse
import xmlrpclib
import re


default_encoding = "text/plain; charset=utf-8"


def main():
    usage = "usage: %prog [options] url"
    parser = optparse.OptionParser(usage)
    parser.add_option("-n", "--namespace", dest="namespace",
                      help="function namespace to use")
    parser.add_option("-e", "--encoding", dest="encoding",
                      default=default_encoding,
                      help='encoding to report [default: "%s"]'
                      % default_encoding)
    parser.add_option("-a", "--argument", dest="filter_args",
                      default=[],
                      help="the name of an XmlRpcFilteringPipe " \
                      "argument, followed by its string value",
                      action="append", type="string", nargs=2)
    parser.add_option("-c", "--content-type", action="store_true",
                      dest="show_content_type", default=False,
                      help="report returned content type on " \
                      "first line")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    
    data = xmlrpclib.Binary(sys.stdin.read())
    filter_args = {}
    for key, val in options.filter_args:
        filter_args[key] = val
    server = xmlrpclib.ServerProxy(args[0])
    function_name = "filterData"
    if options.namespace:
        function_name = "%s.%s" % (options.namespace, function_name)
    result = getattr(server, function_name)(data, options.encoding,
                                            filter_args)
    if options.show_content_type:
        print result["contentType"]
    print result["data"]

    
if __name__ == "__main__":
    main()

