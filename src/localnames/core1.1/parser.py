#!/usr/bin/python2.3
"""
Local Names 1.1 Namespace Description Parser
"""
import re
import urllib


ws_line_re = re.compile( r'^\s*$' )
quoted_column_re = re.compile( r'"\s+(?:(?!\\")[^"]|\\")+"' )
unquoted_column_re = re.compile( r'\s+(?:[^\s]+)' )
record_types = ["LN","NS","X","PATTERN"]

# full, for one column:
#   p=re.compile( r'("(?:(:?(?![\\]")[^"]|[\\]")+)"|(?:[^\s]+))' )
# ...but, it includes outer quotes


def parse_text(text):
    """
    Parse Local Names v1.1 description, and return results and errors.

    Pass UTF-8 text to be parsed. The function returns a tuple with
    the following form:

    (results, errors)

    Results have the form: ("record type", "second column", "third column")
    Errors have the form: (line-number, "human readable error string")
    
    """
    
    def blank(line):
        return ws_line_re.match(line) != None

    def comment(line):
        return len(line) > 0 and line[0] == "#"

    def read_quoted_column(line):
        mo=quoted_column_re.match(line)
        if not mo:
            return ("",
        result = []
        index = 1
        while index < len(line):
            if line[index] == '"':
                return (result,
            if line[index] == "\\":
                result.append(line[index+1])
                index=index+2
            else:
                result.append(

    errors = []
    results = []
    
    lines = text.splitlines()
    lines = zip(range(lines), lines)
    lines = [(num,line) for (num,line) in lines if not blank(line)]
    lines = [(num,line) for (num,line) in lines if not comment(line)]

    for (num,line) in lines:
        first,rest = line.split(None, 1)
        if first not in record_types:
            errors.append((num, "No such record type: %s" % first))
            continue
        # interior pattern, quoted:
        # <- rest
        #    -> errors  <- num, <- line
        #    (CONTINUE!)
        # -> second
        # -> rest
        # rest:   rw
        # second:  w
        # errors: /\
        # num:    r
        # line:   r
        # CONTINUE: possibility: signalled by /\ # of errors
        #### (rest,second,cont)=parse_quoted_column(rest, errors, num, line)
        #### if cont:
        ####    continue
        if rest.starts_with('"'):
            mo=quoted_column_re.match(rest)
            if mo == None:
                errors.append((num, "Can't read second column: %s" % line))
                continue
            second=rest[mo.start()+1:mo.end()-1]
            rest=rest[mo.end():]
        else:
            mo=unquoted_column_re.match(rest)
            if mo == None:
                errors.append((num, "Can't read second column: %s" % line))
                continue
            second=rest[mo.start():mo.end()]
            rest=rest[mo.end():]
        if rest.starts_with('"'):
            mo=quoted_column_re.match(rest)
            if mo == None:
                errors.append((num, "Can't read third column: %s" % line))
                continue
            third=rest[mo.start()+1:mo.end()-1]
            rest=rest[mo.end():]
        else:
            mo=unquoted_column_re.match(rest)
            if mo == None:
                errors.append((num, "Can't read third column: %s" % line))
            third=rest[mo.start():mo.end()]
            rest=rest[mo.end():]
        results.append((first, second, third))
    
    return results, errors

