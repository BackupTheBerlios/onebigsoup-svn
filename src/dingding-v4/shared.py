"""
Event System Shared Code

----

Code shared between various Python modules participating
in the event system.

"""

def stripped_copy( load ):
    """
    Strip out "RESERVED" information from a load.
    """
    copy = load.copy()
    for k in copy.keys():
        if k.startswith( "RESERVED" ):
            del copy[k]
    return copy

def construct_url( hostname, portnumber, path="/" ):
    return "http://%s:%s%s" % (hostname,portnumber,path)
