from Cheetah.Template import Template
import cgi
form = cgi.FieldStorage() # CGI form data


PAGE_KEY = "page"
PAGE_FRONT = "front"
PAGE_EDITSPACES = "editspaces"
PAGE_EDITNAMES = "editnames"
PAGE_EDITOPTS = "editopts"
PAGE_DESCRIPTION = "desc"

SPACE_KEY = "space"
SPACE_GLOBAL = "global"
# key: name of the user's space to work with

ULI_KEY = "uli"


NUM_LOGS_ON_FRONT_PAGE = 20
NUM_LOGS_ON_EDIT_PAGES = 5


LOCALNAMES_IMG='<a href="index.cgi?$PAGE_KEY=$PAGE_DESCRIPTION&$SPACE_KEY=$SPACE"><img style="width: 80px; height: 15px;" alt="Local Names v1.0" src="img_namesv10.png"></a>'
NLSD_IMG='<img style="width: 80px; height: 15px;" alt="nLSD namespace description" src="img_nlsdnames.png">'

def localnames_img():
    t=Template( LOCALNAMES_IMG )
    t.PAGE_KEY = PAGE_KEY
    t.PAGE_DESCRIPTION = PAGE_DESCRIPTION
    t.SPACE_KEY = SPACE_KEY
    t.SPACE = space()
    return str(t)

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

def query_keys_found( keys ):
    for k in keys:
        if not query_dict().has_key( k ):
            return False
    return True

def uli_string():
    return query_dict().get( ULI_KEY )

def page():
    return query_dict().get( PAGE_KEY )

def space():
    result = query_dict().get( SPACE_KEY )
    if result:
        result=result.upper()
    if result == None:
        result=SPACE_GLOBAL
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
    t.LOCALNAMES_IMG = localnames_img()
    t.NLSD_IMG = NLSD_IMG

    t.PAGE = page()
    t.SPACE = space()


# control code - may want to move into code_old
def add_new_names( space, names, url, LN_or_NS="LN" ):
    space = space.upper()
    import code_old
    nsf = code_old.hub.namespace_files.get_space( space )
    if LN_or_NS == "LN":
        nsf.add_names( names, url )
    elif LN_or_NS == "NS":
        nsf.add_namespaces( names, url )
    code_old.hub.event_namesadded( space, names, url )
    nsf.save()

