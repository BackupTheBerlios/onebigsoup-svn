"""DOC

DOC

DOC
Line  -- DOC
quote  -- DOC
unquote  -- DOC
tokenize  -- DOC
"""

import re


re_column = re.compile(r'\s+"(([^\\"]|\\.)+)"')

r'''Read a column.

Ignore white space up to the double-quotation marks. Read out the
inside, all the way up to the other double-quotation marks.

Inside characters are either:
* Not a slash, and not a double-quotation mark. (*)
* A slash, followed by an anything.

De-quoting the interior text will take care of throwing an exception if
you have anything other than \n, \", or \\. (Those are the only legal
slash sequences.)

(*) Newlines will never appear within the double-quotation mark
    region. The parser will always perform a .splitlines() first.
'''

# There are 4 types of records.
#
# These constants are not arbitrary; They _must_ be equivalent to their
# string representations.

LN = "LN"
NS = "NS"
X = "X"
PATTERN = "PATTERN"
record_types = [LN, NS, X, PATTERN]


class Namespace:
    
    """Namespace data and functionality.
    
    DOC
    
    DOC
    """
    
    def __init__(self):
        """Initialize namespace blank.
        
        DOC
        """
	self.data = {LN: OrderedDictionary(),
                     NS: OrderedDictionary(),
                     X: OrderedDictionary(),
                     PATTERN: OrderedDictionary()}
        self.bboard = {}
    
    def __getitem__(self, key):
        """DOC
        
        DOC
        """
        return self.data[key]
    
    def get_bboard(self, name):
        """Get a blackboard of a given name.
        
        A blackboard is an attached dictionary other objects can store
        data in. Every blackboard has a name.
        """
        return self.bboard.setdefault(name, {})
    
    def final(self, args):
        """Return the results of placing args into X "FINAL".
        
        If there is no X "FINAL" entry, return None.
        """
        patterns = self.data["X"].get("FINAL")
        if patterns is None:
            return None
        return UrlTemplate(patterns[0]).replace(args)


class Line:
    
    """Line in a Local Names namespace description.
    
    DOC
    
    DOC
    """
    
    # There are 4 types of lines.
    
    CMT = "COMMENT"
    BLK = "BLANK"
    RCD = "RECORD"
    ERR = "ERROR"
    
    # These are line parse error codes.
    
    ERR_TYPE = 5000
    ERR_KEY = 5001
    ERR_VALUE = 5002
    err_explanations = {ERR_TYPE: "Unrecognized type of line.",
                        ERR_KEY: "Can't decypher the key.",
                        ERR_VALUE: "Can't decypher the value."}
    
    def __init__(self, text=None):
        """DOC
        
        DOC
        """
        self.clear()
        if text is not None:
            self.decode(text)
    
    def clear(self):
        """Blank the state data."""
        self.line_type = None
        self.record_type = None
        self.key = None
        self.value = None
        self.text = None  # Original parsed line text
        self.error = None  # Line.ERR_xxx
    
    def decode(self, text):
        """Decode a line of text, and store it.
        
        Return True if the line is a Local Names namespace description
        line, False if it doesn't not parse right.
        """
        self.clear()
        self.text = text
        if text == "":
            self.line_type = Line.BLK
            return True
        elif text[0] == "#":
            self.line_type = Line.CMT
            return True
        for x in record_types:  # Match
            if text.startswith(x):
                self.line_type = Line.RCD
                self.record_type = x  # Store
        if self.line_type is None:  # Abort
            self.line_type = Line.ERR  # Not a blank, comment, or record
            self.error = Line.ERR_TYPE
            return False
	remainder = text[len(self.record_type):]  # Get text
        match = re_column.match(remainder)  # Match
        if match is None:  # Abort
            self.line_type = Line.ERR  # No column 2
            self.error = Line.ERR_KEY
            return False
        self.key = match.group(1)  # Store
        remainder = remainder[len(match.group(0)):]  # Get text
        match = re_column.match(remainder)  # Match
        if match is None:  # Abort
            self.line_type = Line.ERR  # No column 3
            self.error = Line.ERR_VALUE
            return False
        self.value = match.group(1)  # Store
        return True
    
    def __str__(self):
        """Render equivalent namespace description text.
        
        Record lines are constructed from record_type, key, and value.
        All other lines are constructed from stored line text.
        """
        if self.line_type in [Line.CMT, Line.ERR, Line.BLK]:
            return self.text
        elif self.line_type != Line.RCD:
            return None
        return self.record_type + " " + \
               quote(self.key) + " " + quote(self.value)


class OrderedDictionary:
    
    """Dictionary with ordered keys.
    
    Keys are ordered in a list. As keys are defined, they are added (or
    relocated) to the end of the list. You can also define keys at the
    beginning of the list.
    
    __getitem__  -- read value from dictionary
    __setitem__  -- append item to dictionary
    __delitem__  -- delete item from dictionary
    get  -- read value from dictionary with default
    setdefault  -- get, use a default if necessary
    append  -- append item to dictionary
    insert  -- insert item into dictionary
    """
    
    def __init__(self):
        """Initialize a blank dictionary."""
        self.data = {}
        self.order = []
    
    def __getitem__(self, key):
        """Read an value from the dictionary."""
        return self.data[key]
    
    def __setitem__(self, key, value):
        """Append a value to the dictionary."""
        self.append(key, value)
    
    def __delitem__(self, key):
        """Delete an item."""
        if key in self.data:
            del self.data[key]
            self.order.remove(key)
    
    def get(self, key, default=None):
        """Read a value from the dictionary, or return a default."""
        if key in self.data:
            return self.data[key]
        return default
    
    def setdefault(self, key, default=None):
        if self.data.has_key(key):
            return self.data[key]
        self[key] = default
        return default
    
    def append(self, key, value):
        """Append a key-value pair to the dictionary."""
        del self[key]
        self.data[key] = value
        self.order.append(key)
    
    def insert(self, key, value, index=0):
        """Insert key-value pair into dictionary at given location."""
        del self[key]
        self.data[key] = value
        self.order.insert(index, key)  # TODO: check arg order


class UrlTemplate:
    
    """URL template, with $NAME and $ARGn replacement.
    
    DOC
    
    DOC
    """
    
    def __init__(self, text):
        """Initialize URL template with particular text.
        
        DOC
        """
        self.text = text
    
    def replace(self, args):
        """DOC"""
        if not isinstance(args, list):
            args = [args]
        text = self.text.replace("$NAME", args[0])
        n = 1
        while True:
            argnum = "$ARG%d" % n
            if argnum in text:
                text = text.replace(argnum, args[n-1])
                n = n + 1
            else:
                return text


def quote(text):
    """Quote a string for use in column 2 or column 3."""
    text = text.replace("\\", "\\\\")
    text = text.replace("\n", "\\n")
    text = text.replace('"', '\\"')
    return '"' + text + '"'


def unquote(text):
    """Unquote a string found in column 2 or column 3.
    
    If the text is surrounded by quotation marks, they are stripped.
    """
    if text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    letters = []
    quoting = False
    for ch in text:
        if quoting:  # following a slash (\)
            if ch not in ["n", "\\", '"']:
                raise SyntaxError("invalid escape sequence")
            if ch == "n":
                letters.append("\n")
            else:
                letters.append(ch)
            quoting = False
        else:
            if ch == "\n":
                raise SyntaxError("newline in string")
            elif ch == '"':
                raise SyntaxError("quotation marks in string")
            elif ch == "\\":
                quoting = True
            else:
                letters.append(ch)
    return "".join(letters)


def tokenize(text):
    """Tokenize a v1.2 Local Names namespace description into lines.
    
    text must be Python unicode. Remember that the Local Names Namespace
    Description Specification version 1.2 says that namespace
    descriptions must be encoded in UTF-8.
    
    DOC
    """
    results = []
    for x in text.splitlines():
        line = Line(x)
        results.append(line)
    return results


def lines_to_namespace(lines):
    """DOC
    
    DOC
    """
    ns = Namespace()
    for line in lines:
        if line.line_type != Line.RCD:
            continue
        if line.record_type in ["LN", "NS", "PATTERN"]:
            ns[line.record_type][line.key] = line.value
        else:
            ns[X].setdefault(line.key, []).append(line.value)
    return ns


if __name__ == "__main__":
    TODO

