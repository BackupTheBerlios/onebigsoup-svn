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

def url_for_page( page_name ):
    import conf
    t=Template( "http://%s%sindex.cgi?$PAGE_KEY=%s&$SPACE_KEY=$SPACE" % (conf.URL_DOMAIN_NAME,
                                                                         conf.URL_DIRECTORY_BASE,
                                                                         page_name) )
    inform_template(t)
    return str(t)

def has_password():
    import code_old
    if space() == None:
        return False
    return code_old.hub.space_notes.has_password( space() )

def query_string():
    import os
    return os.environ.get( "QUERY_STRING", "" )

def query_dict():
    import os, cgi
    return cgi.parse_qs( query_string() )

def query_keys_found( keys ):
    for k in keys:
        if not query_dict().has_key( k ):
            return False
    return True

def uli_string():
    return query_dict().get( ULI_KEY, [None] )[0]

def page():
    return query_dict().get( PAGE_KEY, [None] )[0]

def space():
    result = query_dict().get( SPACE_KEY, [None] )[0]
    if result:
        result=result.upper()
    if result == None:
        result=SPACE_GLOBAL
    return result

def password():
    result = query_dict().get( PASSWORD, [None] )[0]
    if result:
        return result
    result = form[ "password" ][0].value

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

