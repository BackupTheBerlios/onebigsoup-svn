"""
Publish nLSD graph
"""

import sys
import pickle

all_lists = []
LISTS_PICKLE_FILENAME = "lists.p"
WEB_SERVICE_URL = "http://services.taoriver.net:9303/"

PermReadWrite = 1
PermReadOnly = 0

class InvalidParameter(Exception):
    def __init__( self, param_name ):
        self.param_name = param_name
        Exception.__init__(self, "Paramater is invalid: %s" % self.param_name)

class AbstractListClass:
    def __init__(s):
        s.title = "(Programming error, Abstract list Class)"
        s.local_name = None
    def __len__(s):
        raise "Need to define in subclass."
    def filter_out_outofbounds_indexes(s, given_indexes ):
        possible_indexes=range(0,len(s))
        valid=[]
        invalid=[]
        for x in given_indexes:
            if x in possible_indexes:
                valid.append( x )
            else:
                invalid.append( x )
        return (valid,invalid)
    def show_lines(s, indexes):
        response=[str(s[i])+"\n" for i in indexes]
        return "".join(response)
    def get_localnames(s):
        results = []
        if s.local_name:
            results.append(s.local_name)
        if s.title:
            results.append(s.title)
        return results
    
class MasterList(AbstractListClass):
    """
    This is the master list of lists.

    Commands that may interact w/ this object:
    show, head, tail, all, 
    """
    def __init__(s):
        AbstractListClass.__init__(s)
        s.title = "List of Lists"
    def __len__(s):
        return len(all_lists)
    def __getitem__(s, i):
        return all_lists[i]

class ListObject(AbstractListClass):
    """
    This is a list that the user has created.
    """
    def __init__(s, title=None):
        AbstractListClass.__init__(s)
        s.id=len(all_lists)
        all_lists.append(s)
        s.title=title
        s.rw=PermReadWrite
        s.entries=[]
        s.cursor=0
        s.list_cursor = 0
        s.adminpwd="subwoofer"
        s.checklist=False
    def __len__(s):
        return len(s.entries)
    def __getitem__(s, i):
        return s.entries[i]
    def __str__(s):
        return "%3d. %s" % (s.id, s.title or "(no title)")
    def id_of_entry(s, entry):
        return s.entries.index(entry)
    def cap(s):
        s.rw=PermReadOnly
        return s
    def uncap(s):
        s.rw=PermReadWrite
        return s
    def show_lines(s, indexes):
        t = s.title or "(no title)"
        return t+"\n"+AbstractListClass.show_lines(s, indexes)

    def check(s, index):
        s.entries[index].checked = True
        s.checklist = True

    def uncheck(s, index):
        s.entries[index].checked = True


class Entry:
    def __init__(s, listobject, line):
        s.lo = listobject
        s.line_data=line
        s.checked=False
        s.lo.entries.append(s)

    def __str__(s):
        if s.lo.checklist==False:
            return "%3d. %s" % (s.get_id(), s.line_data)
        else:
            return "%3d. %s %s" % (s.get_id(), {True:"(./)", False:"(  )"}[s.checked], s.line_data)

    def get_id(s):
        return s.lo.id_of_entry(s)


class Tokenizer:
    def __init__(s, string_to_wrap):
        s.data = string_to_wrap
    def peek_token(s):
        eaten = s.data.split(None, 1)
        return eaten[0]
    def barf_token(s, barf):
        s.data = barf + " " + s.data
    def eat_token(s):
        """
        Use this to return the first part of "string_to_wrap"
        and assign the remainder if any back to s.data
        """
        eaten = s.data.split(None, 1)
        if len(eaten)==0: return None
        if len(eaten)==1:
            eaten.append("")
            (token, s.data) = eaten
            return token
        if len(eaten)==2:
            (token, s.data) = eaten
            return token
    def rest(s):
        return s.data
    def eat_int(s):
        """
        Use this function if you're expecting an int as the
        first part of "string_to_wrap"
        """
        return int(s.eat_token())
    def eat_listno(s):
        """
        Use this function to retrieve the list number from the
        input line. It raises a custom exception if it encounters
        a problem
        """
        ln = s.eat_token()
        try:
            return int(ln)
        except TypeError:
            raise InvalidParameter("List Number is None")
        except ValueError:
            raise InvalidParameter("List Number is not an Integer")
    def eat_complex_selection(s):
        instructions = s.data.split(",")
        entrylist = []
        for x in instructions:
            if (not ":" in x) and (not "-" in x):
                entrylist.append(int(x))
            else:
                if ":" in x:
                    (start,end)=x.split(":")
                else:
                    (start, end) = x.split("-")
                start,end=(int(start),int(end))
                if start>end:
                    entrylist.extend(range(start,end-1,-1))
                else:
                    entrylist.extend(range(start,end+1))
        s.data = ""
        return entrylist


class TestData:
    def __init__(s):
        lo=ListObject()
        for ld in range(0,15):
            entry = Entry(lo, "Test"+str(ld))

def get(path):
    response = []
    if path == ["localnames"]:
        response.append("# This is an uli_list local names description file")
        response.append("# visit http://purl.net/net/localnames/ to learn more about local names")
        mlo = MasterList()
        response.append( '# this document' )
        response.append( 'LN this %s%s' % (WEB_SERVICE_URL,"localnames/") )
        response.append( '# master List of Lists' )
        response.append( 'LN lists %s' % WEB_SERVICE_URL )
        response.append( 'LN "list of lists" %s' % WEB_SERVICE_URL )
        response.append( 'LN ListOfLists %s' % WEB_SERVICE_URL )
        if mlo.local_name != None:
            ln = mlo.local_name
            if " " in ln:
                ln = '"%s"' % ln
            response.append("LN %s %s" % (ln, WEB_SERVICE_URL))
        response.append( '# individual lists' )
        for lo in mlo:
            for ln in lo.get_localnames():
                if " " in ln:
                    ln = '"%s"' % ln
                response.append("LN %s %s" % (ln, WEB_SERVICE_URL+str(lo.id)+"/"))
        return "\n".join(response)+"\n"

    response.append("<html><head><title>Uli Lists</title></head>")
    response.append("<body>")
    if len(path) == 1:
        lo = all_lists[int(path[0])]
        response.append('<a href="%s">List of Lists</a>  ---  <a href="%s%s">LocalNames</a>\n<h3>List %s</h3>(local name: %s)<ul>' % (WEB_SERVICE_URL, WEB_SERVICE_URL, "localnames/", str(lo), lo.local_name or "no local name"))
        for item in lo:
            response.append("<li>%s</li>" % str(item))
    else:
        mlo = MasterList()
        response.append('<a href="%s%s">Local Names</a><h3>List of Lists</h3>\n<ul>' % (WEB_SERVICE_URL, "localnames/"))
        for lo in mlo:
            response.append('<li><a href="%s%d/">%d - %s </a></li>' % (WEB_SERVICE_URL, lo.id, lo.id, lo.title))
    response.append("</ul>")
    response.append('<p><form method="post" action="%s%s">' % (WEB_SERVICE_URL, "uliform/"))
    response.append('<a href="http://onebigsoup.wiki.taoriver.net/moin.cgi/UniversalLineInterface">uli:</a> <input type="text" name="uli"></form></p>')
    response.append("</body></html>")
    return "\n".join(response)+"\n"


def uli(line):
    def get_lo_or_master():
        if tok.peek_token().lower()=="lists":
            tok.eat_token()
            lo = MasterList()
        else:
            lo = all_lists[tok.eat_listno()]
        return lo
    tok = Tokenizer(line)
    cmd = tok.eat_token().lower()
    if tok.rest()==None: return "Just hitting enter won't get you anywhere ;)"
    msg = "I don't know how to handle %s" % line
    if cmd=="help":
        msg = "help, localname lst# word, show lst# indexes, new, rename lst# name, cap/uncap lst#, head lst#, tail lst#, all lst#, add lst# line, add# lst# num, check/uncheck lst# indexes -- lst# can be 'lists', indexes of form 3, 7, 9:19"
    elif cmd=="localname":
        lo = get_lo_or_master()
        lo.local_name = tok.rest()
        msg = "Local name set to %s" % lo.local_name
    elif cmd=="show":
        """
        Will allow a user to show a list item or a list of list items,
        including ranges as in the check/uncheck commands. It will also
        allow the user to see all checked or all unchecked items.
        """
        lo = get_lo_or_master()
        indexes = tok.eat_complex_selection()
        valid, invalid = lo.filter_out_outofbounds_indexes(indexes)
        msg = lo.show_lines(valid)
    elif cmd=="new":
        lo = ListObject()
        if tok.rest()=="":
            msg = "List created: #%d" % (lo.id)
        else:
            lo.title=tok.eat_token()
            msg = "List created: #%d (%s)" % (lo.id, lo.title)
    elif cmd=="rename":
        lo = all_lists[tok.eat_listno()]
        title = tok.rest()
        lo.title = title
        msg = "List " + str(lo.id) + " renamed to " + str(lo.title)
    elif cmd=="cap":
        lo = all_lists[tok.eat_listno()]
        lo.cap()
        if lo.title==None:
            t = ""
        else:
            t = " (" + lo.title + ")"
        msg = "List #%d%s was capped" % (lo.id, t)
    elif cmd=="head":
        """
        This will return up to the first 5 items in the list. It will
        ignore any input past the command and the list number
        """
        lo = get_lo_or_master()
        msg = lo.show_lines(range(5))
    elif cmd=="tail":
        lo = get_lo_or_master()
        start=len(lo)-5
        end=len(lo)
        if start < 1: start=0
        msg = lo.show_lines(range(start,end))
    elif cmd=="all":
        lo = get_lo_or_master()
        start=0
        end=len(lo)
        msg = lo.show_lines(range(start, end))
    elif cmd=="uncap":
        lo = all_lists[tok.eat_listno()]
        pwd = tok.eat_token()
        if pwd!=None:
            pwd = pwd.strip()
        if lo.adminpwd==pwd:
            lo.uncap()
            msg = "List #%d (%s) was uncapped" % (lo.id, lo.title)
        else:
            msg = "Password invalid"
    elif cmd=="add":
        lo = all_lists[tok.eat_listno()]
        entry = Entry(lo, tok.rest())
        msg = "Added"
    elif cmd=="add#":
        lo = all_lists[tok.eat_listno()]
        entry = Entry( lo, tok.eat_int() )
        msg = "Added"
    elif cmd in ("check", "uncheck"):
        lo = all_lists[tok.eat_listno()]
        candidates = tok.eat_complex_selection()
        (valids, invalids) = lo.filter_out_outofbounds_indexes(candidates)
        for x in valids:
            if cmd=="check": lo.check(x)
            elif cmd=="uncheck": lo.uncheck(x)
        msg = ""
        if len(valids) > 0:
            msg = msg + {"check":"Items checked ", "uncheck":"Items unchecked "}[cmd] + ",".join([str(x) for x in valids]) + ".\n"
        if len(invalids) > 0:
            msg = msg + "Invalid indexes " + ",".join([str(x) for x in invalids]) + ".\n"
    pickle.dump(all_lists, open(LISTS_PICKLE_FILENAME, "w"))
    return msg

def load_pickle():
    global all_lists
    try:
        all_lists = pickle.load( open( LISTS_PICKLE_FILENAME ) )
    except IOError:
        all_lists = []
    

def main():
    load_pickle()
    if all_lists == []:
        TestData()
    while True:
        input = raw_input("ULILIST> ")
        if input.upper()=="QUIT":
            print "Have a nice day"
            break
        print uli(input)

if __name__ == "__main__":
#    main()
    import http_server
    load_pickle()
    
    http_server.run( "ULI List Server",
                     "services.taoriver.net", 9303,
                     uli_func=uli, get_func=get )
