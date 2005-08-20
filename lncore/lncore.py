"""DOC

DOC

DOC
url_to_text  -- DOC
text_to_lines  -- DOC
lines_to_namespace  -- DOC
combine  -- DOC
url_to_namespace  -- DOC
quote  -- DOC
unquote  -- DOC
Namespace  -- DOC
Store  -- DOC
Traditional  -- DOC
Line  -- DOC
OrderedDictionary  -- DOC
KeyHashOrderedDictionary  -- DOC
UrlTemplate  -- DOC
"""

import re
import sets

import urllib


punctuation_re = re.compile(r'[^A-Za-z0-9\s]+', re.UNICODE)
ws_re = re.compile(r'\s+', re.UNICODE)
the_re = re.compile(r'\b(?:the|a|an|in|for)\b', re.UNICODE|re.IGNORECASE)

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


def url_to_text(url):
    """Given a URL of UTF-8 text, return the text."""
    return urllib.urlopen(url).read().decode('utf-8')


def text_to_lines(text):
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


def combine(f, g):
    return lambda x:f(g(x))


url_to_namespace = combine(lines_to_namespace,
                           combine(text_to_lines, url_to_text))


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


def traditional_hash(name):
    """Prepare name for loose comparison as in Traditional Style.

    Returns the name in lower case, without any punctuation, white
    space, trailing "s", "int", "ed", or articles the, a, and an.
    """
    name = name.lower()
    name = punctuation_re.sub("", name)
    name = ws_re.sub("", name)
    try:
        if name.endswith("s"):
            name=name[:-1]
        if name.endswith("ing"):
            name=name[:-3]
        if name.endswith("ed"):
            name=name[:-2]
        the_re.sub("",name)
    except IndexError:
        pass
    return name


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


class Store:
    
    """Namespace store.
    
    DOC
    
    DOC
    """
    
    def __init__(self, builder=url_to_namespace):
        """Create a namespace store.
        
        builder is a function (or something that can be called like a
        function) that accepts a url, and returns a namespace.
        """
        self.cache = {}
        self.builder = builder
    
    def __call__(self, url):
        """Get a namespace from the store.
        
        If it's cached, return it from the cache. If not, build it, and
        then return it.
        """
        if url in self.cache:
            return self.cache[url]
        ns = self.builder(url)
        self.cache[url] = ns
        return ns


class Traditional:
    
    """Traditional style resolution.
    
    DOC
    
    DOC
    """
    
    def __init__(self, store):
        """DOC
        
        DOC
        """
        self.store = store
    
    def bboard(self, ns):
        """DOC"""
        bb = ns.get_bboard("Traditional")
        if "SETUP" in bb:
            return bb
        bb[NS] = KeyHashOrderedDictionary()
        bb[LN] = KeyHashOrderedDictionary()
        bb[X] = KeyHashOrderedDictionary()
        bb[PATTERN] = KeyHashOrderedDictionary()
        bb[NS].load_from(ns[NS])
        bb[LN].load_from(ns[LN])
        bb[X].load_from(ns[X])
        bb[PATTERN].load_from(ns[PATTERN])
        bb["SETUP"] = True
        return bb
    
    def find(self, url, path, record_type):
        """DOC
        
        DOC
        """
        if isinstance(path, basestring):
            path = [path]
        try:
            ns = self.store(url)
        except IOERROR:
            return (-TODO, TODO)
        
        if len(path) == 1:
            return self.last_pathentry(url, path[0], record_type)
        
        bb = self.bboard(ns)
        ns_result = ns[NS].get(path[0])  # Lookup NS record literally.
        ns_loose = False
        if ns_result is None:  # It wasn't there; Try loose.
            ns_result = bb[NS].get(path[0])
            ns_loose = True
        pattern_result = ns[PATTERN].get(path[0])
        pattern_loose = False
        if pattern_result is None:  # It wasn't there; Try loose.
            pattern_result = bb[PATTERN].get(path[0])
            pattern_loose = True
        
        if ns_result and not ns_loose:
            use = "ns"
        elif pattern_result and not pattern_loose:
            use = "pattern"
        elif ns_result:
            use = "ns"
        elif pattern_result:
            use = "pattern"
        else:
            use = None
        
        if use == "pattern":
            pattern = UrlTemplate(pattern_result)
            return (0, pattern.replace(path[1:]))
        
        if use == "ns":
            return self.find(ns_result, path[1:], record_type)
        
        return (-TODO, TODO)
    
    def last_pathentry(self, url, name, record_type):
        """DOC
        
        DOC
        """
        ns = self.store(url)
        bb = self.bboard(ns)
        
        result = self.look_through(url, record_type, name)
        if result:
            return (0, result)
        
        # It wasn't found here, so we're going to check the neighbors.
        
        explored = sets.Set()
        for neighbor_key in ns[NS].order():
            neighbor_url = ns[NS][neighbor_key]
            if neighbor_url not in explored:
                result = self.look_through(neighbor_url,
                                           record_type, name)
                if result is not None:
                    return (0, result)
                explored.add(neighbor_url)
        
        # It wasn't found in neighbors; try X FINAL?
        
        if record_type == LN:
            result = ns.final(name)
            if result is not None:
                return (0, result)
        
        # It simply wasn't found.
        
        return (-TODO, TODO)
    
    def look_through(self, url, record_type, key):
        """Perform a quick look through a namespace, looking for a key.
        
        Look for the key first as it is, then key-hashed. If it's not
        found, return None.
        
        NO special treatment here- if it's not found, return None. No
        looking through neighboring namespaces, or anything like that.
        """
        ns = self.store(url)
        bb = self.bboard(ns)
        result = ns[record_type].get(key)
        if result is not None:
            return result
        return bb[record_type].get(key)
    
    def TODO(self, TODO):
        """DOC
        
        DOC
        """
        TODO


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
    order  -- get order of keys
    """
    
    def __init__(self):
        """Initialize a blank dictionary."""
        self._data = {}
        self._order = []
    
    def __getitem__(self, key):
        """Read an value from the dictionary."""
        return self._data[key]
    
    def __setitem__(self, key, value):
        """Append a value to the dictionary."""
        self.append(key, value)
    
    def __delitem__(self, key):
        """Delete an item."""
        if key in self._data:
            del self._data[key]
            self._order.remove(key)
    
    def get(self, key, default=None):
        """Read a value from the dictionary, or return a default."""
        if key in self._data:
            return self._data[key]
        return default
    
    def setdefault(self, key, default=None):
        """DOC"""
        if self._data.has_key(key):
            return self._data[key]
        self[key] = default
        return default
    
    def append(self, key, value):
        """Append a key-value pair to the dictionary."""
        del self[key]
        self._data[key] = value
        self._order.append(key)
    
    def insert(self, key, value, index=0):
        """Insert key-value pair into dictionary at given location."""
        del self[key]
        self._data[key] = value
        self._order.insert(index, key)  # TODO: check arg order
    
    def order(self):
        """Return a copy of the key order list."""
        return self._order + []


class KeyHashOrderedDictionary:
    
    """Ordered Dictionary that hashes keys before use.
    
    Work by wrapping an OrderedDictionary with a call to a key-hashing
    function. Keys are hashed on both storage and retrieval.
    
    __getitem__  -- read value from dictionary
    __setitem__  -- append item to dictionary
    __delitem__  -- delete item from dictionary
    get  -- read value from dictionary with default
    setdefault  -- get, use a default if necessary
    append  -- append item to dictionary
    insert  -- insert item into dictionary
    """
    
    def __init__(self, hash_function=traditional_hash):
        """Initialize a blank dictionary.
        
        Optionally specify the hashing function. If none chosen, use the
        Traditional Style hash function.
        """
        self._hash = hash_function
        self._data = OrderedDictionary()
    
    def __getitem__(self, key):
        """Read an value from the dictionary."""
        return self._data[self._hash(key)]
    
    def __setitem__(self, key, value):
        """Append a value to the dictionary."""
        self._data[self._hash(key)] = value
    
    def __delitem__(self, key):
        """Delete an item."""
        del self._data[self._hash(key)]
    
    def get(self, key, default=None):
        """Read a value from the dictionary, or return a default."""
        return self._data.get(self._hash(key), default)
    
    def setdefault(self, key, default=None):
        """DOC"""
        return self._data.setdefault(self._hash(key), default)
    
    def append(self, key, value):
        """Append a key-value pair to the dictionary."""
        return self._data.append(self._hash(key), value)
    
    def insert(self, key, value, index=0):
        """Insert key-value pair into dictionary at given location."""
        return self._data.insert(self._hash(key), value, index)
    
    def load_from(self, ordered_dict):
        """Load data from an ordered dictionary."""
        for x in ordered_dict.order():
            self[x] = ordered_dict[x]
    
    def order(self):
        """Return a copy of the key order list."""
        return self._data.order()


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


if __name__ == "__main__":
    TODO

