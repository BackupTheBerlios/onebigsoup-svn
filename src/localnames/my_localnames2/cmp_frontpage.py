from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_frontpage.html" )

def response():
    logs_data = code_old.hub.activity_log.get_logs( code_info.NUM_LOGS_ON_FRONT_PAGE )
    
    code_info.inform_template(t)
    t.html_notes = [ x["msg"] for x in logs_data ]

    return str(t)


