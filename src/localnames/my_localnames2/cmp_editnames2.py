from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_editnames2.html" )

def subtitle():
    return "Names"

def response():
    qd = code_info.query_dict()
    if qd.has_key( "url" ) and qd.has_key( "name" ):
        
    code_info.inform_template(t)
    return str(t)


