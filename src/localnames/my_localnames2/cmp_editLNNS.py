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

def alts():
    if qd.has_key( "alt" ):
        if type( qd[ "alt" ] ) == type( "" ):
            return [ qd[ "alt" ] ]
        elif type( qd[ "alt" ] ) == type( [] ):
            return qd[ "alt" ]
    else:
        return []

def names():
    if qd.has_key( "name" ):
        n = [ qd["name"] ] # names
    else:
        n = []
    n.extend( alts() )
    return n

def url():
    if qd.has_key( "url" ):
        return qd["url"]
    else:
        return None


def register_new_names():
    if code_info.query_keys_found( ["url", "name", code_info.SPACE_KEY ] ):
        if LN_or_NS == "LN":
            space_file.add_names( names(), url() )
        elif LN_or_NS == "NS":
            space_file.add_namespaces( names(), url() )
        else:
            raise "this should never happen"
        code_old.hub.event_namesadded( code_info.space(), names(), url() )
        space_file.save()

def register_checked_names():
    for key in code_info.form.keys():
        if key.startswith( "EXTRA-" ):
            name=key[ 6: ]
            if LN_or_NS == "LN":
                if name == "this":
                    url = "http://to-be-coded"
                elif name == "edit":
                    url = "http://to-be-coded"
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

    if LN_or_NS == "LN":
        extras_in_order = extra_file.get_names_in_order()
        extras_in_order.insert( 0, ( "this", "http://to-be-coded" ) )
        extras_in_order.insert( 0, ( "edit", "http://to-be-coded" ) )
    elif LN_or_NS == "NS":
        extras_in_order = extra_file.get_namespaces_in_order()

    t.EXTRA = [ { "NAME": entry[0],
                  "URL": entry[1] }
                for entry in extras_in_order
                if entry[0] not in [x[0] for x in in_order] ]

    return str(t)


