import urllib, xmlrpclib

def uli_http( url, line ):
    return urllib.urlopen( url, urllib.urlencode( {"ULI":line} ) )

def uli_xmlrpc( url, line ):
    return xmlrpclib.ServerProxy( url ).uli( line )
