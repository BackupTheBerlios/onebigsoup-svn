from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_editnames.html" )

def response():
    
    code_info.inform_template(t)
    return str(t)

