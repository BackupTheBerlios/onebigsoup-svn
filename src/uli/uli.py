import urllib, xmlrpclib

def uli_http( url, line ):
    urllib.urlopen( url, urllib.urlencode( {"ULI":line} ) )

def uli_xmlrpc( url, line ):
    xmlrpclib.ServerProxy( url ).uli( line )
