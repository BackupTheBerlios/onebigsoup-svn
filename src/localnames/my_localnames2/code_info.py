
PAGE_KEY = "page"
PAGE_FRONT = "front"
PAGE_EDITSPACES = "editspaces"
PAGE_EDITNAMES = "editnames"
PAGE_EDITOPTS = "editopts"
PAGE_DESCRIPTION = "desc"

SPACE_KEY = "space"
# key: name of the user's space to work with

ULI_KEY = "uli"


NUM_LOGS_ON_FRONT_PAGE = 20
NUM_LOGS_ON_EDIT_PAGES = 5


LOCALNAMES_IMG='<img style="width: 80px; height: 15px;" alt="Local Names v1.0" src="img_namesv10.png"><br>'
NLSD_IMG='<img style="width: 80px; height: 15px;" alt="nLSD namespace description" src="img_nlsdnames.png">'

def query_string():
    import os
    return os.environ.get( "QUERY_STRING", "" )

def query_dict():
    import os, cgi
    _dict = cgi.parse_qs( query_string() )
    for (k,v) in _dict.items():
        if type(v) == type([]) and len(v)==1:
            _dict[k]=v[0]
    return _dict

def uli_string():
    return query_dict().get( ULI_KEY )

def page():
    return query_dict().get( PAGE_KEY )

def space():
    result = query_dict().get( SPACE_KEY )
    if result:
        result=result.upper()
    return result

def blank_request():
    return len( query_dict() ) == 0

def inform_template( t ):
    t.PAGE_KEY = PAGE_KEY
    t.PAGE_FRONT = PAGE_FRONT
    t.PAGE_EDITSPACES = PAGE_EDITSPACES
    t.PAGE_EDITNAMES = PAGE_EDITNAMES
    t.PAGE_EDITOPTS = PAGE_EDITOPTS
    t.SPACE_KEY = SPACE_KEY
    t.LOCALNAMES_IMG = LOCALNAMES_IMG
    t.NLSD_IMG = NLSD_IMG

    t.PAGE = page()
    t.SPACE = space()


# control code - may want to move into code_old
def add_new_names( space, names, url ):
    import code_old
    nsf = code_old.hub.namespace_files.get_space( space )
    nsf.add_names( names, url )
    code_old.hub.event_namesadded( space, names, url )

