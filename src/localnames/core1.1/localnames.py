"""
Local Names 1.1 Server
"""
import time
import urllib
import re
import sets
import cgi

import lnparser


store = {}
time_to_live = 24*60*60  # one day

punctuation_re = re.compile(r'[^A-Za-z0-9\s]+', re.UNICODE)
ws_re = re.compile(r'\s+', re.UNICODE)
the_re = re.compile(r'\b(?:the|a|an|in|for)\b', re.UNICODE|re.IGNORECASE)
link_re = re.compile(r'\[((?:\[.+?\])+)([^\]]+?)?\]',
                     re.MULTILINE|re.IGNORECASE|re.UNICODE|re.DOTALL)
softlink_re = re.compile(r'\(((?:\(.+?\))+)([^\)]+?)?\)',
                         re.MULTILINE|re.IGNORECASE|re.UNICODE|re.DOTALL)

loose_flags = sets.ImmutableSet(["no-case", "no-punctuation",
                                 "no-space", "forgive-spelling"])

standard_X_keys = ["FINAL", "VERSION", "AUTHOR", "AUTHOR-FOAF",
                   "LAST-CHANGED", "PREFERRED-NAME"]


def dump_cache(url):
    """Dump cache entry for a particular url."""
    try:
        del store[url]
    except KeyError:
        pass


def preferred_names():
    """
    Dictionary linking cached namespace preferred name to url.

    Old cache entries discarded, then
    names assigned first come first serve.

    """
    decorated = [(ns["TIME"], ns) for ns in store.values()]
    decorated.sort()
    spaces = [ns for ns_time, ns in decorated]
    
    now = time.time()
    for space in spaces:
        if now > space["TIME"] + time_to_live:
            dump_cache(space["URL"])
        else:
            break

    bindings = {}
    not_found_num = 0
    for space in spaces:
        found = False
        for name in space["X"].get("PREFERRED-NAME", []):
            if not bindings.has_key(name):
                bindings[name] = space["URL"]
                found = True
                break
        if not found:
            while bindings.has_key("anonymous%3d" % not_found_num):
                not_found_num = not_found_num + 1
            bindings["anonymous%3d" % not_found_num] = space["URL"]
            not_found_num = not_found_num + 1
    return bindings


def get_namespace(url):
    """
    Returns a namespace dictionary.

    Returns a cached version if possible,
    retrieves fresh from the web otherwise.

    The namespace dictionary is structured so:

    "TIME": (INTERNAL) cache timestamp
    "URL": url used to fetch namespace
    "TEXT": raw UTF-8 text cached
    "ERRORS": list of parse errors;
              each error is a tuple:
              (line#,"error msg")
    "LN-raw": raw list of parsed LN entries (line#,"2nd-col", "3rd-col")
    "NS-raw": (same) 
    "PATTERN-raw": (same)
    "X-raw": (same)
    "LN": dictionary of LN entries {"name":"URL"}
    "NS": (same)
    "PATTERN": (same)
    "X": dictionary of X entries, {"name":["one","two",...]}

    """
    now = time.time()
    try:
        if now < store[url]["TIME"] + time_to_live:
            return store[url]
    except KeyError:
        pass
    
    namespace = {}
    namespace["TIME"] = now
    namespace["URL"] = url
    namespace["TEXT"] = urllib.urlopen( url ).read().decode("utf-8","replace")

    (results, errors) = lnparser.parse_text(namespace["TEXT"])

    namespace["ERRORS"] = errors
    namespace["LN-raw"] = []
    namespace["NS-raw"] = []
    namespace["PATTERN-raw"] = []
    namespace["X-raw"] = []
    for line_number, record_type, second, third in results:
        namespace[record_type+"-raw"].append((line_number, second, third))

    namespace["LN"] = {}
    namespace["NS"] = {}
    namespace["PATTERN"] = {}
    namespace["X"] = {}
    for record_type in ["LN", "NS", "PATTERN"]:
        for line_number, second, third in namespace[record_type+"-raw"]:
            if not namespace[record_type].has_key(second):
                namespace[record_type][second] = third
            else:
                msg = "redefinition of %s" % second
                namespace["ERRORS"].append((line_number, msg))
    for line_number, second, third in namespace["X-raw"]:
        namespace["X"].setdefault(second, []).append(third)

    store[url] = namespace
    return namespace


def aggregate(urls):
    """
    Aggregate several namespaces into one.

    Aggregation is mostly simple:
    Pure concatenation of text files;
    With one exception:
    An "aggregation" block appears at the
    bottom of the file, that lists sources
    of aggregation like so:

      X AGGREGATES "URL"
      X AGGREGATES "URL"
      (and so on and so forth)

    """
    namespaces = [get_namespace(url) for url in urls]

    super_text = [ns["TEXT"] for ns in namespaces]
    for url in urls:
        super_text.append(u'X AGGREGATES "%s"\n' % url)

    namespace = {}
    namespace["TIME"] = time.time()
    namespace["URL"] = None
    namespace["TEXT"] = "".join(super_text)

    (results, errors) = lnparser.parse_text(namespace["TEXT"])
    
    namespace["ERRORS"] = errors
    namespace["LN-raw"] = []
    namespace["NS-raw"] = []
    namespace["PATTERN-raw"] = []
    namespace["X-raw"] = []
    for ns in namespaces:
        for record_type in ["LN-raw", "NS-raw", "PATTERN-raw", "X-raw"]:
            namespace[record_type].extend(ns[record_type])

    namespace["LN"] = {}
    namespace["NS"] = {}
    namespace["PATTERN"] = {}
    namespace["X"] = {}
    for record_type in ["LN", "NS", "PATTERN"]:
        for line_number, second, third in namespace[record_type+"-raw"]:
            if not namespace[record_type].has_key(second):
                namespace[record_type][second] = third
    for line_number, second, third in namespace["X-raw"]:
        if second not in standard_X_keys:
            namespace["X"].setdefault(second, []).append(third)
        elif second == "FINAL":
            if not namespace["X"].has_key("FINAL"):
                namespace["X"]["FINAL"] = [third]
        elif second in ["AUTHOR", "AUTHOR-FOAF"]:
            namespace["X"].setdefault(second,[]).append(third)
    
    namespace["X"]["VERSION"] = ["1.1"]
    isotime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    namespace["X"]["LAST-CHANGED"] = [isotime]
    namespace["X"]["PREFERRED-NAME"] = ["aggregate"]

    return namespace


def lookup(path, url, flags):
    """
    Resolve a path to a URL.

    Returns the resolved URL.

    path: ["space", "space", ..., "name"]
    url: "http://url.to.first.namespace.description/"
    flags: Python 2.3 Set of flags

    The following flags are understood:

      "no-case":  ignore capitalization
      "no-punctuation":  ignore punctuation
      "no-space":  ignore white space
      "forgive-spelling":  accept plausible mis-spellings
      "loose": "no-case" + "no-punctuation" + "no-space"
               + "check-neighboring-spaces" +
      "check-neighboring-spaces":  check spaces linked by NS
      "reverse":  reverse lookup (URL, not name, at end of path)
      "NS":  namespace-lookup; (NS, not LN, at end of path)

    """
    if "loose" in flags:
        flags = flags | loose_flags
        flags.discard("loose")
    assert len(path) > 0
    namespace = get_namespace(url)

    if len(path) == 1:
        if "NS" in flags:
            records = namespace["NS-raw"]
        else:
            records = namespace["LN-raw"]

        # If "loose" flags are being used, try resolving without loose
        # flags, first.  If there is an exact match, it has priority.

        if flags & loose_flags:
            result = _check_list(path[0], records, flags - loose_flags)
            if result:
                return result

        result = _check_list(path[0], records, flags)
        if result:
            return result

        if "check-neighboring-spaces" in flags:
            wo_neighboring = flags.copy()
            wo_neighboring.discard("check-neighboring-spaces")
            urls = sets.Set()
            for num, neighborname, url in namespace["NS-raw"]:
                if url not in urls:
                    result = lookup(path[0], url, wo_neighboring)
                    if result:
                        return result
                    urls.add(url)

        if ("FINAL" in namespace["X"]) and ("reverse" not in flags):
            return namespace["X"][0].replace("$PAGE", path[0])
        return None
    else:
        pattern_raw = namespace["PATTERN-raw"]
        ns_raw = namespace["NS-raw"]
        original_flags = flags
        flags = flags.copy()
        flags.discard("reverse")
        if flags & loose_flags:
            result = _check_list(path[0], pattern_raw, flags - loose_flags)
            if result:
                return result.replace("$PAGE", path[1])
            result = _check_list(path[0], ns_raw, flags - loose_flags)
            if result:
                return lookup(path[1:], result, original_flags)

        result = _check_list(path[0], pattern_raw, flags)
        if result:
            return result.replace("$PATH", path[1])
        result = _check_list(path[0], ns_raw, flags)
        if result:
            return lookup(path[1:], result, original_flags)

        return None


def _check_list(name, records, flags):
    """
    Lookup a name in one of the namespace's raw lists.

    Returns None if no matches found.
    Returns the first match found, otherwise.
    "reverse" searches return a list of matches.

    name:  name to look for
    records:  list of (line#, name, URL) to search
    flags:  list of strings representing flags

    Recognized flags: "no-case", "no-punctuation", "no-space",
                      "forgive-spelling", "reverse"

    """
    pname = _prepare_key(name, flags)
    reversed = "reverse" in flags
    forgive_spelling = "forgive-spelling" in flags
    reversed_list = []

    for num, second, third in records:
        if reversed:
            second, third = third, second
        psecond = _prepare_key(second, flags)
        if pname == psecond:
            if reversed:
                reversed_list.append( third )
            else:
                return third
        if forgive_spelling:
            pass  # not coded yclass HostNotFound(Exception):

    if reversed:
        if len(reversed_list) > 0:
            return reversed_list
    return None


def _prepare_key(name, flags):
    """
    Prepares a key for comparison.

    name: string,  flags: list of strings
    Recognized flags: "no-case", "no-punctuation",
                      "no-space", "forgive-spelling".

    """
    if "no-case" in flags:
        name = name.lower()
    if "no-punctuation" in flags:
        name = punctuation_re.sub("", name)
    if "no-space" in flags:
        name = ws_re.sub("", name)
    if "forgive-spelling" in flags:
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


def display_namespace_text(namespace):
    """Write namespace's cached text to the console."""

    lines = namespace["TEXT"].splitlines()
    for num, line in enumerate(lines):
        print "#%3d:  %s" % (num, line.encode("ascii","replace"))


def display_namespace_errors(namespace):
    """Write namespace's cached errors to the console."""
    lines = namespace["TEXT"].splitlines()
    for num, msg in namespace["ERRORS"]:
        print "  %3d:  %s" % (num, msg.encode("ascii","replace"))
        print "        %s" % lines[num].encode("ascii","replace")


def replace_text(text, namespace_url, softlink_base=""):
    """
    Replace links denoted by [[foo]] with A HREFs.

    text:  text to make replacements in
    namespace_url:  URL of namespace to start from
    softlink_base:  URL base to softlink from

    Examples:
        [[some name]]
        [[NS link][NS link][LN name]]
        [[some name]some other text covering it]
        [[NS link][LN name]some other text]

    Softlinks have the form:
      ((foo)(bar))
    ...which becomes a link to:
      (SOFTLINK_BASE)?action=redir&url=(URL)&lookup=foo&lookup=bar
    """

    def replace_link(match):
        flags = sets.Set(["loose", "check-neighboring-spaces"])
        path = match.group(1)[1:-1].split('][')
        url = lookup(path, namespace_url, flags)
        title = match.group(2)
        if title == None:
            title = path[-1]
        return '<a href="%s">%s</a>' % (url, cgi.escape(title))

    def replace_softlink(match):
        flags = sets.Set(["loose", "check-neighboring-spaces"])
        path = match.group(1)[1:-1].split(')(')
        map = {'action': 'redir', 'url': namespace_url, 'lookup': path}
        url = softlink_base + "?" + urllib.urlencode(map, True)
        title = match.group(2)
        if title == None:
            title = path[-1]
        return '<a href="%s">%s</a>' % (url, cgi.escape(title))

    text = link_re.sub(replace_link, text)
    text = softlink_re.sub(replace_softlink, text)
    return text


if __name__ == '__main__':
    url = "http://ln.taoriver.net/localnames.txt"
    namespace = get_namespace(url)
    display_namespace_text(namespace)
    print
    print "ERRORS:"
    display_namespace_errors(namespace)
    print "LOOKUPS:"
    flags = sets.Set()
    print "Wiki Wrapper:", lookup(["Wiki Wrapper"], url, flags)
    flags.add("reverse")
    print "reverse:",
    print lookup(["http://wrap.localnames.taoriver.net/"], url, flags)
    print "loose (wiki-wrappers):",
    flags.add("loose")
    flags.discard("reverse")
    print lookup(["wiki-wrappers"], url, flags)
    get_namespace("http://taoriver.net/tmp/gmail.txt")
    print "Preferred Names:",
    print preferred_names()
    text = '[[Local Names]] is a project that [[Lion]] is working on.'
    print text
    print replace_text(text, "http://ln.taoriver.net/localnames.txt")
    text = 'I really like [[Local Names]this project.]'
    print text
    print replace_text(text, "http://ln.taoriver.net/localnames.txt")
    text = 'You need to use [[X]an X record] to do that.'
    print text
    print replace_text(text, "http://ln.taoriver.net/localnames.txt")
    text = 'This is ((soft linked)) text. We\'ll use a' \
           '((name server)) to resolve it at click-time.'
    print text
    print replace_text(text, "http://ln.taoriver.net/localnames.txt")
    print aggregate(["http://taoriver.net/tmp/gmail.txt", "http://ln.taoriver.net/localnames.txt"])

