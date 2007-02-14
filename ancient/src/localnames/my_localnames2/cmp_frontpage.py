from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_frontpage.html" )

def response():
    import cmp_activity
    t.ACTIVITY = cmp_activity.response( code_info.NUM_LOGS_ON_FRONT_PAGE )
    code_info.inform_template(t)
    return str(t)


