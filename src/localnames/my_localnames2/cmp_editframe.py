from Cheetah.Template import Template
import code_info

t = Template( file="cmp_editframe.html" )

BOLD_SPAN = '<span style="font-weight: bold;">'
SPAN_CLOSE = '</span>'

# utility function, for internal use
def ahref( page ):
    return '<a href="index.cgi?%s=%s&%s=%s">' % ( code_info.PAGE_KEY,
                                                  page,
                                                  code_info.SPACE_KEY,
                                                  code_info.space() )

def response():
    code_info.inform_template(t)
    t.NAMES_OPEN = ahref( code_info.PAGE_EDITNAMES )
    t.NAMES_CLOSE = "</a>"
    t.SPACES_OPEN = ahref( code_info.PAGE_EDITSPACES )
    t.SPACES_CLOSE = "</a>"
    t.OTHER_OPEN = ahref( code_info.PAGE_EDITOPTS )
    t.OTHER_CLOSE = "</a>"
    if code_info.page() == code_info.PAGE_EDITNAMES:
        import cmp_editnames2
        cmp=cmp_editnames2
        t.NAMES_OPEN=BOLD_SPAN
        t.NAMES_CLOSE=SPAN_CLOSE
    elif code_info.page() == code_info.PAGE_EDITSPACES:
        t.SPACES_OPEN=BOLD_SPAN
        t.SPACES_CLOSE=SPAN_CLOSE
    elif code_info.page() == code_info.PAGE_EDITOPTS:
        t.OTHER_OPEN=BOLD_SPAN
        t.OTHER_CLOSE=SPAN_CLOSE
    else:
        pass # illegal
    t.EDIT_SECTION_NAME = cmp.subtitle()
    t.EDIT_SECTION = cmp.response()
    return str(t)

