
from mod_python import apache

def requesthandler( req ):
    req.content_type = "text/plain"
    req.write( "Hello, World!" )
    return apache.OK
