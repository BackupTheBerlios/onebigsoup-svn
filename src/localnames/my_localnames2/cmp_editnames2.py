from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_editnames2.html" )

def subtitle():
    return "Names"

def register_new_names():
    qd = code_info.query_dict()
    if qd.has_key( "url" ) and qd.has_key( "name" ) and qd.has_key( code_info.SPACE_KEY ):
        space = qd[ code_info.SPACE_KEY ]
        url = qd[ "url" ]
        names = [ qd[ "name" ] ]
        if qd.has_key( "alt" ):
            if type( qd[ "alt" ] ) == type( "" ):
                new_names.append( qd[ "alt" ] )
            elif type( qd[ "alt" ] ) == type( [] ):
                new_names.extend( qd[ "alt" ] )
        code_info.add_new_names( space, names, url )

def response():
    register_new_names()

    code_info.inform_template(t)

    name_of_space = code_info.space()
    space_file=code_old.hub.namespace_files.get_space( name_of_space )
    names_in_order=space_file.get_names_in_order()

    t.NAMES=[]
    for (index, kv) in enumerate( names_in_order ):
        (name,url) = kv
        t.NAMES.append( { "INDEX": index,
                          "NAME": name,
                          "URL": url, } )

    return str(t)
#    return repr( space_file )



