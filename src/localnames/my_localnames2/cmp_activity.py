from Cheetah.Template import Template
import code_info
import code_old

t = Template( file="cmp_activity.html" )

def response( num_logs ):
    logs_data = code_old.hub.activity_log.get_logs( num_logs )
    t.html_notes = [ x["msg"] for x in logs_data ]
    
    code_info.inform_template(t)

    return str(t)


