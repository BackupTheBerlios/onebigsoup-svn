from Cheetah.Template import Template
import code_info
import code_old

LN_or_NS = "unconfigured" # invoking module sets to "LN" or "NS"


t = Template( file="cmp_editLNNS.html" )

space_file=code_old.hub.namespace_files.get_space( code_info.space().upper() )
extra_file=code_old.hub.namespace_files.get_space( "EXTRA" )
qd = code_info.query_dict()


def subtitle():
    return { "LN": "Names",
             "NS": "Spaces" }[ LN_or_NS ]

def names():
    n = qd.get( "name", None ) + qd.get( "alt", [] )
    return n


def register_new_names():
    if code_info.query_keys_found( ["url", "name", code_info.SPACE_KEY ] ):
        if LN_or_NS == "LN":
            space_file.add_names( names(), qd.get( "url", None ) )
        elif LN_or_NS == "NS":
            space_file.add_namespaces( names(), qd.get( "url", None ) )
        else:
            raise "this should never happen"
        code_old.hub.event_namesadded( code_info.space(), names(), qd.get( "url", None ) )
        space_file.save()

def register_checked_names():
    for key in code_info.form.keys():
        if key.startswith( "EXTRA-" ):
            name=key[ 6: ]
            if LN_or_NS == "LN":
                if name == "this":
                    url = code_info.url_for_page( code_info.PAGE_DESCRIPTION )
                elif name == "edit":
                    url = code_info.url_for_page( code_info.PAGE_EDITNAMES )
                else:
                    url=extra_file.get_names()[name]
                space_file.add_name( name, url )
            elif LN_or_NS == "NS":
                url=extra_file.get_namespaces()[name]
                space_file.add_namespace( name, url )
            else:
                raise "this should never happen - note: afkpes"
            space_file.save()

def gval( k,i ):
    """
    value of form entries;
    of the form: string#

    ex: gval( "foo", 4 )
    ...returns form value "foo4"
    """
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
    register_checked_names()
    if code_info.form.has_key( "NUM_ENTRIES0" ):
        register_changes_deletes_reorders()

    code_info.inform_template(t)

    t.NAME_OR_NAMESPACE = { "LN":"a Name for a Link",
                            "NS":"a Name for a Namespace" }[ LN_or_NS ]
    t.NAMES_OR_NAMESPACES = { "LN":"Names for Links",
                              "NS":"Names for Namespaces" }[ LN_or_NS ]
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

    if LN_or_NS == "LN":
        extras_in_order = extra_file.get_names_in_order()
        extras_in_order.insert( 0, ( "this", code_info.url_for_page( code_info.PAGE_DESCRIPTION ) ) )
        extras_in_order.insert( 0, ( "edit", code_info.url_for_page( code_info.PAGE_EDITNAMES ) ) )
    elif LN_or_NS == "NS":
        extras_in_order = extra_file.get_namespaces_in_order()

    t.EXTRA = [ { "NAME": entry[0],
                  "URL": entry[1] }
                for entry in extras_in_order
                if entry[0] not in [x[0] for x in in_order] ]

    return str(t)


