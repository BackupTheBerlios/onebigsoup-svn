__all__ = ['http_post', 'http_get', 'http', 'xmlrpc', 'forms_by_name', 'form_names', 'prompt']

import urllib, xmlrpclib

# urllib.urlopen ignores HTTP errors and doesn't tell us about them, so we use urllib.URLopener which is less smart.

# I hear that urllib2 would be better.

def _check_http_response( response ):
   ctype = response.info()["Content-Type"]
   if ctype.split(";")[0] == "text/plain":
      return response.read()
   else:
      raise IOError, "Wrong Content-Type for ULI response: %s" % ctype

def http_post( url, line ):
   uo = urllib.URLopener()
   response = uo.open( url, urllib.urlencode( {"ULI":line} ) )
   return _check_http_response(response)

# for backwards compatibility
http = http_post

def http_get( urlPrefix, line ):
   uo = urllib.URLopener()
   response = uo.open( urlPrefix + urllib.quote(line, "") )
   ctype = response.info()["Content-Type"]
   return _check_http_response(response)

def xmlrpc( url, line ):
    return xmlrpclib.ServerProxy( url ).uli( line )

forms_by_name = { 
  "http":      http_get,
  "http_get":  http_get,
  "http-get":  http_get,
  "get":       http_get,
  "http_post": http_post,
  "http-post": http_post,
  "post":      http_post,
  "xmlrpc":    xmlrpc,
  "xml-rpc":   xmlrpc,
  "xml_rpc":   xmlrpc,
}

form_names = {
  http_get:  "http_get",
  http_post: "http_post",
  xmlrpc:    "xmlrpc",
}

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
