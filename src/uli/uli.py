import urllib, xmlrpclib

def http( url, line ):
   # urllib.urlopen ignores HTTP errors and doesn't tell us about them
   uo = urllib.URLopener()
   response = uo.open( url, urllib.urlencode( {"ULI":line} ) )
   ctype = response.info()["Content-Type"]
   if ctype == "text/plain":
      return response.read()
   else:
      raise IOError, "Wrong Content-Type for ULI response: %s" % ctype

def xmlrpc( url, line ):
    return xmlrpclib.ServerProxy( url ).uli( line )

def prompt( prompt_string, uli_url, call_func ):
    """
    prompt_string: ex: "<uli-9095> "

    uli_url:       ex: "http://services.taoriver.net:9095/"

    call_func:     uli.http or uli.xmlrpc
    """
    input = ""

    while input.upper() != "QUIT":
        input = raw_input( prompt_string )
        if input.upper() != "QUIT":
            print call_func( uli_url, input )
