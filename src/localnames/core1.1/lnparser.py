#!/usr/bin/python2.3
"""
Local Names 1.1 Namespace Description Parser
"""
import re
import urllib


ws_line_re = re.compile(r'^\s*$')
record_type_re = re.compile(r'[.]|LN|NS|X|PATTERN', re.IGNORECASE)
column_re = re.compile(r'\s+("(?:(:?(?![\\]")[^"]|[\\]")+)"|(?:[^\s]+))', re.UNICODE)


class LocalNamesSyntaxError(Exception):
    def __init__(self, msg):
        self.msg=msg
        Exception.__init__(self, 'Local Names v1.1 Syntax Error: %s" % msg')


def escape(text):
    r'''Replace \ with \\, replace " with \".'''
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    return text


def unescape(text):
    r'''Replace \\ with \, replace \" with ".'''
    text = text.replace('\\"', '"')
    text = text.replace('\\\\', '\\')
    return text


def parse_text(text):
    """
    Parse Local Names v1.1 description, and return results and errors.

    Pass UTF-8 text to be parsed. The function returns a tuple with
    the following form:

    (results, errors)

    Results have the form: (line#, "record type", "second column", "third column")
    Errors have the form: (line#, "human readable error string")
    
    """
    
    def blank(line):
        return ws_line_re.match(line) != None

    def comment(line):
        return len(line) > 0 and line[0] == "#"

    def parse_record_type(cursor, line, parsed):
        mo=record_type_re.match(line[cursor:])
        if mo == None:
            raise LocalNamesSyntaxError("unrecognized v1.1 record type- require LN, NS, X, or PATTERN")
        parsed.append(mo.group())
        return cursor+mo.end()

    def parse_column(cursor, line, parsed, col_num):
        mo=column_re.match(line[cursor:])
        if mo == None:
            raise LocalNamesSyntaxError("poorly formatted column #%d" % col_num)
        text=mo.group(1)
        if text[0] == u'"':
            text = text[1:-1]
        parsed.append(text)
        return cursor+mo.end()

    errors = []
    results = []
    
    lines = text.splitlines()
    nlines = zip(range(len(lines)), lines)
    nlines = [(num,line) for (num,line) in nlines if not blank(line)]
    nlines = [(num,line) for (num,line) in nlines if not comment(line)]

    for num,line in nlines:
        try:
            parsed=[]
            cursor=0
            cursor=parse_record_type(cursor,line,parsed)
            cursor=parse_column(cursor,line,parsed,2)
            cursor=parse_column(cursor,line,parsed,3)
            for index in [0,1,2]:
                if parsed[index] == ".":
                    try:
                        parsed[index] = results[-1][index+1]
                    except IndexError:
                        errors.append((num, "no previous column"))
            results.append((num,parsed[0],parsed[1],parsed[2]))
        except LocalNamesSyntaxError, exc:
            errors.append((num, exc.msg))
    
    return results, errors


test_string = u"""
# test string for parser

X version 1.1

LN "Lion Kimbro" http://www.speakeasy.org/~lion/
LN "with \\"quotes\\" inside" http://google.com/
. . .

this line is an error
"""

if __name__ == '__main__':
    import pprint
    for num, line in enumerate(test_string.splitlines()):
        print "#%2d:  %s" % (num, line)
    pprint.pprint(parse_text(test_string))

