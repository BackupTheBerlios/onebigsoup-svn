from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_editLNNS.html" )

space_file=code_old.hub.namespace_files.get_space( code_info.space() )

LN_or_NS = "unconfigured" # invoking module sets to "LN" or "NS"

def subtitle():
    return { "LN": "Names",
             "NS": "Spaces" }[ LN_or_NS ]


def register_new_names():
    qd = code_info.query_dict()
    if qd.has_key( "url" ) and qd.has_key( "name" ) and qd.has_key( code_info.SPACE_KEY ):
        space = qd[ code_info.SPACE_KEY ]
        url = qd[ "url" ]
        names = [ qd[ "name" ] ]
        if qd.has_key( "alt" ):
            if type( qd[ "alt" ] ) == type( "" ):
                names.append( qd[ "alt" ] )
            elif type( qd[ "alt" ] ) == type( [] ):
                names.extend( qd[ "alt" ] )
        code_info.add_new_names( space, names, url, LN_or_NS )

def gval( k,i ):
    if code_info.form.has_key( k+str(i) ):
        return code_info.form[ k+str(i) ].value
    return None

def get_order_and_bindings():
    X = [ ( float(gval("ORDER",i)),
            gval("NAME",i),
            gval("URL",i) )
          for i in range( int(gval("NUM_ENTRIES",0)) )
          if not gval("DEL",i) ]
    X.sort()
    in_order = [x[1] for x in X]
    to_urls = {}
    for (i,name,url) in X:
        to_urls[name]=url
    return (in_order,to_urls)

def register_changes_deletes_reorders():
    (in_order,to_urls) = get_order_and_bindings()
    space_file.replace_names( in_order, to_urls, LN_or_NS )
    space_file.save()



def response():
    register_new_names()
    if code_info.form.has_key( "NUM_ENTRIES0" ):
        register_changes_deletes_reorders()

    code_info.inform_template(t)

    t.NAME_OR_NAMESPACE = { "LN":"Name",
                            "NS":"Namespace" }[ LN_or_NS ]
    t.PAGE_VALUE = { "LN": code_info.PAGE_EDITNAMES,
                     "NS": code_info.PAGE_EDITSPACES }[ LN_or_NS ]

    if LN_or_NS == "LN":
        in_order=space_file.get_names_in_order()
    elif LN_or_NS == "NS":
        in_order=space_file.get_namespaces_in_order()

    t.NAMES=[]
    for (index, kv) in enumerate( in_order ):
        (name,url) = kv
        t.NAMES.append( { "INDEX": index,
                          "NAME": name,
                          "URL": url, } )
    t.NUM_ENTRIES = len( t.NAMES )

    return str(t)


