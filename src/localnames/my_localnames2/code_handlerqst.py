import code_info

def text_html():
    return "Content-type: text/html\n\n"

import cgitb
cgitb.enable()

import code_old
# in code_old, it will open the main pickle file

if (code_info.page() == code_info.PAGE_FRONT) or (code_info.blank_request()):
    import cmp_frontpage
    print text_html()
    print cmp_frontpage.response()
elif code_info.page() == code_info.PAGE_EDITNAMES:
    import cmp_editframe
    print text_html()
    print cmp_editframe.response()
    #import cmp_editnames
    #print text_html()
    #print cmp_editnames.response()
else:
    print text_html()
    print "<p>not made yet</p>"
    print "<p>received:", str(code_info.query_dict()), "</p>"

# save out the main pickle file
code_old.hub.pickle.save()
