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
    return str(t)


