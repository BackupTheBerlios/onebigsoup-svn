from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_editnames2.html" )

def subtitle():
    return "Names"

def register_new_names():
    qd = code_info.query_dict()
    if qd.has_key( "url" ) and qd.has_key( "name" ) and qd.has_key( code_info.SPACE_KEY ):
        nsf = code_old.hub.namespace_files.get_space( qd[ code_info.SPACE_KEY ] )
        new_names = [ qd["name"] ]
        if qd.has_key( "alt" ):
            if type( qd["alt"] ) == type( "" ):
                new_names.append( qd["alt"] )
            elif type( qd["alt"] ) == type( [] ):
                new_names.extend( qd["alt"] )
        nsf.add_names( new_names, qd["url"] )
        code_old.hub.event_namesadded( qd[ code_info.SPACE_KEY ],
                                       new_names,
                                       qd[ "url" ] )

def response():
    register_new_names()
    code_info.inform_template(t)
    return str(t)


