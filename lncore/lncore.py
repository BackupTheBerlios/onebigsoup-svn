"""DOC

DOC

TODO: adjust tests to use TestStore.

DOC
text_to_lines  -- DOC
lines_to_namespace  -- DOC
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

import webcache


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

styles = []

"""Registered styles.

Register every style class in the styles dictionary above. The first
listed style is the default style.

Each style should define info and find(url, path, record_type).

DOC: Describe info and the find functions in more depth.
"""


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

    def preferred_name(self):
        """Return the preferred name, as found in X "PREFERRED-NAME".

        If there is none, return None.
        """
        return self.data["X"].get("PREFERRED-NAME",[None])[0]


class Store:
    
    """Internet-based Namespace store.

    The Store contains a page cache, and a namespace cache.
    
    The page cache associates web pages and timeouts with every URL. The
    page cache is intended to be a webcache.WebCache instance. If you
    leave the page cache at it's default None, a webcache.WebCache will
    be created.
    
    The namespace cache associates lncore.Namespace instances with every
    URL. What about timeouts for namespace data? We just rely on the
    page cache's timeouts to tell us when to dump a namespace cache
    entry.
    
    DOC
    
    DOC
    """
    
    def __init__(self, page_cache=None):
        """Create namespace store that retrieves, stores pages by cache.

        Pass a new webcache.WebCache in as the page_cache argument,
        unless you have made your own object that meets the same
        interface.
        """
        self.ns_cache = {}  # Namespaces cache.
        self.page_cache = page_cache
        if self.page_cache is None:
            self.page_cache = webcache.WebCache()
    
    def __call__(self, url):
        """Get a namespace from the store.

        If the namespace is cached, and hasn't timed out- return it. If
        not, get the page from the page cache, build a namespace from
        it, and return it.
        """
        if ((url in self.ns_cache) and \
            (self.page_cache.time_to_live(url) > 0)):
            return self.ns_cache[url]
        ns_text = self.page_cache.get_page(url).decode('utf-8')
        lines = text_to_lines(ns_text)
        ns = lines_to_namespace(lines)
        self.ns_cache[url] = ns
        return ns
    
    def get_cached_text(self, ns_url):
        """Get the unicode text of a cached namespace description."""
        if ((url not in self.ns_cache) or
            (self.page_cache.time_to_live(ns_url) <= 0)):
            return (-302, "not cached")
        return (0, self.page_cache.get_page(ns_url))
    
    def time_to_live(self, url):
        """Return the number of seconds before a namespace times out."""
        return self.page_cache.time_to_live(url)
    
    def get_cache_list(self):
        """Return list of information about the cache.

        By "the cache," we don't just mean the namespace cache
        (ns_cache), we also mean the full page cache.

        If the server has been rebooted, and the ns_cache is empty, but
        the disk cache is full- beware: This can be a potentially very
        costly operation..! It'll open up every namespace, interpret it,
        and cache it in memory. It does that, because it pulls the X
        "PREFERRED-NAME" record out, if it's there.
        
        DOC - based on "CACHE" in lnquery.get_server_info.

        DOC
        """
        self.clean()
        results = []
        for url in self.page_cache:
            preferred_name = self(url).preferred_name() or ""
            ttl = self.time_to_live(url)
            results.append((preferred_name, url, ttl))
        return results
    
    def clean(self):
        """Vet cache of expired entries.
        
        Internally, call this to make sure that the namespaces and names
        lists are in sync with the webcache. Externally, you can call
        this if you think you might clear up some memory.
        """
        self.page_cache.clean()
        for url in self.ns_cache:
            if url not in self.page_cache:
                del self.ns_cache[url]

    def dump_cache(self, url):
        """DOC

        DOC
        """
        found = False
        if url in self.ns_cache:
            del self.ns_cache[url]
        if url in self.page_cache:
            self.page_cache.dump(url)
            found = True
        return found


class TestStore:

    """A Namespace store for use when testing.

    The store does not go to the Internet. Rather, it constructs
    namespaces from constant text.

    DOC
    """
    
    def __init__(self):
        """DOC"""
        self.namespaces = {}

    def bind(self, url, ns_text):
        """DOC

        ns_text must be unicode.
        """
        lines = text_to_lines(ns_text)
        ns = lines_to_namespace(lines)
        self.namespaces[url] = ns
        ns.get_bboard("STORE")["TEXT"] = ns_text

    def __call__(self, url):
        """Get a namespace from the store.

        Return None if there is no such namespace.
        """
        return self.namespaces.get(url)

    def get_cached_text(self, url):
        """Get the unicode text of a namespace description."""
        if url not in self.namespaces:
            return None
        return self.namespaces[url].get_bboard("STORE")["TEXT"]

    def get_cache_list(self):
        """Return list of information about the cache.

        DOC
        """
        results = []
        for url in self.namespaces:
            preferred_name = self(url).preferred_name() or ""
            ttl = self.time_to_live(url)
            results.append((preferred_name, url, ttl))
        return results
    
    def time_to_live(self, url):
        """Always return 1000 seconds. (They never expire in here.)"""
        return 1000


class Traditional:
    
    """Traditional style resolution.
    
    DOC
    
    DOC
    """

    info = ["traditional",
            "This is the normal way of resolving names, described in"
            " the Local Names XML-RPC Query Interface specification."]
    
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
            return (-300, "cannot read namespace description: %s" % url)
        
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
        
        return (-201, "record not found: %s" % path[0])
    
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
                result = self.look_through(neighbor_url.encode('utf-8'),
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
        
        return (-201, "record not found: %s" % name)
    
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


styles.append(Traditional)


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

