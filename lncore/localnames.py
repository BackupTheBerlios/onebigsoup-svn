"""Local Names v1.1 Server

dump_cache -- dump cache entry
preferred_names -- list names of cached namespaces
get_namespace -- cache a namespace
aggregate -- form a namespace from several namespaces
clean -- render a "clean" description of a namespace
lookup -- resolve a path to a URL
replace_text -- add <A HREF's> to a text based on lookups
"""
import time
import urllib
import re
import sets
import cgi

import lnparser


image_extensions = [".png", ".jpeg", ".jpg", ".gif"]

store = {}
time_to_live = 7*24*60*60  # one week

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


def isotime():
    """Time in ISO8601 form: yyyy-mm-ddThh:mm:ss form."""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


def dump_cache(url):
    """Dump cache entry for a particular url."""
    try:
        del store[url]
        return True
    except KeyError:
        return False


def preferred_names():
    """Get namespace URLs by PREFERRED-NAME.
    
    Returns a dictionary linking cached namespace preferred name to the
    namespace's url.

    Old cache entries are discarded, and then names are assigned on a
    first come first serve basis.
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


def _namespace_from_text(text):
    """
    Returns namespace dictionary given some UTF-8 text.
    
    The namespace dictionary is structured so:

    "TIME": (INTERNAL) cache timestamp
    "URL": url used to fetch namespace - to be filled out by caller
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
    "LN-loose": dictionary of LN entries {"loose name":"URL"}
    "NS-loose": (same)
    "PATTERN-loose": (same)
    "X-loose": (same)

    """
    (results, errors) = lnparser.parse_text(text)

    namespace = {}
    namespace["TIME"] = time.time()
    namespace["URL"] = None
    namespace["TEXT"] = text
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
    namespace["LN-loose"] = {}
    namespace["NS-loose"] = {}
    namespace["PATTERN-loose"] = {}
    namespace["X-loose"] = {}
    for record_type in ["LN", "NS", "PATTERN"]:
        for line_number, second, third in namespace[record_type+"-raw"]:
            if not namespace[record_type].has_key(second):
                namespace[record_type][second] = third
                namespace[record_type+"-loose"][_prepare_key(second)] = third
            else:
                msg = "redefinition of %s" % second
                namespace["ERRORS"].append((line_number, msg))
    for line_number, second, third in namespace["X-raw"]:
        namespace["X"].setdefault(second, []).append(third)

    return namespace


def get_namespace(url):
    
    """Retrieve a namespace.
    
    Returns a namespace dictionary.

    Returns a cached version if possible, retrieves fresh from the web
    otherwise.
    """
    
    now = time.time()
    try:
        if now < store[url]["TIME"] + time_to_live:
            return store[url]
    except KeyError:
        pass

    text = urllib.urlopen(url).read().decode("utf-8", "replace")
    namespace = _namespace_from_text(text)
    namespace["URL"] = url

    store[url] = namespace
    return namespace


def aggregate(urls):
    """
    Aggregate several namespaces into one.

    Aggregation is mostly simple:
    Pure concatenation of text files.

    At the head of the concatenation is a
    summary of the aggregation, like so:

      X PREFERRED-NAME "aggregate"
      X LAST-CHANGED "yyyy-mm-ddThh:mm:ss"
      X AGGREGATES "URL"
      X AGGREGATES "URL"
      ...
    """
    super_text = []
    super_text.append(u'X PREFERRED-NAME "aggregate"\n')
    super_text.append(u'X LAST-CHANGED "%s"\n' % isotime())
    for url in urls:
        super_text.append(u'X AGGREGATES "%s"\n' % url)
    for url in urls:
        super_text.append(get_namespace(url)["TEXT"])
    return _namespace_from_text("".join(super_text))


def clean(namespace):
    """
    Returns a clean VERSION 1.1 rendition of a namespace.

    Data is seperated into four blocks: X, LN, PATTERN, and NS.
    Within blocks, original order is preserved.
    Standard X keys are handled particularly and intelligently.
    X LAST-CHANGED is updated to the present time.
    """
    text = []

    def show_wo_repeating(key):
        """Write X records, but don't repeat any values."""
        if key not in namespace["X"]:
            return
        vals = namespace["X"][key]
        shown = []
        for val in vals:
            if val not in shown:
                shown.append(val)
                text.append(u'X %s %s\n' % (key, lnparser.escape(val)))
    
    text.append(u'X VERSION 1.1\n')
    text.append(u'X LAST-CHANGED %s\n' % isotime())
    show_wo_repeating("PREFERRED-NAME")
    show_wo_repeating("AUTHOR")
    show_wo_repeating("AUTHOR-FOAF")
    if "FINAL" in namespace["X"]:
        final = lnparser.escape(namespace["X"]["FINAL"][0])
        text.append(u'X FINAL %s\n' % final)

    for record_type in ["X", "LN", "PATTERN", "NS"]:
        covered = []
        for line_num, second, third in namespace[record_type+"-raw"]:
            if record_type == "X":
                if second in standard_X_keys:
                    continue
            elif second in covered:
                continue
            covered.append(second)
            text.append(u'%s %s %s\n' % (record_type,
                                         lnparser.escape(second),
                                         lnparser.escape(third)))
        if len(namespace[record_type+"-raw"]) > 0:
            text.append(u'\n')

    return ''.join(text)


def lookup(path, url, flags, success_path = None):
    """
    Resolve a path to a URL.

    Returns the resolved URL.
    If the search failed, returns a tuple.  (see below)

    path: ["space", "space", ..., "name"]
    url: "http://url.to.first.namespace.description/"
    flags: Python 2.3 Set of flags
    success_path: (used internally for recursion)

    The following flags are understood:

      "loose": ignore case, ignore punctuation, ignore white space
      "check-neighboring-spaces":  check spaces linked by NS
      "reverse":  reverse lookup (URL, not name, at end of path)
      "NS":  namespace-lookup; (NS, not LN, at end of path)
      "suppress-final":  don't use "X FINAL"

    Failure Tuple:

    Upon failure, returns a tuple of the following form:

      1. (list) [URL-of-successful load, NS-of-successful lookup, ...]
      2. (string) failure type: "NS" lookup, "LN" lookup, or "LOAD" failure
      3. (string) name of failed NS or LN lookup, or URL of failed LOAD
      4. (string) human readable error string

    If you re doing a reverse lookup, there is no such thing as an
    "LN" failure type;  You get either a list of names, an empty list (no
    matches,) or an NS or LOAD error.
    
    """
    if success_path == None:
        success_path = list()
    
    flags = sets.Set(flags)
    assert len(path) > 0
    try:
        namespace = get_namespace(url)
    except IOError:
        return (success_path, "LOAD", url,
                'unable to load namespace "%s"' % url)
    success_path.append(url)
    pname = _prepare_key(path[0])

    if len(path) == 1:
        if "NS" in flags:
            record_type = "NS"
        else:
            record_type = "LN"

        if not "reverse" in flags:
            result = namespace[record_type].get(path[0])
            if result:
                return result
            if "loose" in flags:
                result = namespace[record_type+"-loose"].get(pname)
            if result:
                return result
        else:
            found = []
            for num, name, url in namespace[record_type+"-raw"]:
                if name == url:
                    found.append(name)
                elif pname == _prepare_key(url):
                    found.append(name)

        if "check-neighboring-spaces" in flags:
            wo_neighboring = flags.copy()
            wo_neighboring.discard("check-neighboring-spaces")
            wo_neighboring.add("suppress-final")
            urls = sets.Set()
            for num, neighborname, url in namespace["NS-raw"]:
                if url not in urls:
                    result = lookup([path[0]], url, wo_neighboring, [])
                    if type(result) in [type(u'unicode'), type(u'string')]:
                        return result
                    if "reverse" in flags:
                        found.extend( result)
                    urls.add(url)

        if "reverse" in flags:
            return found

        if record_type == "LN" and not "suppress-final" in flags \
           and "reverse" not in flags:
            final = namespace["X-loose"].get(_prepare_key("FINAL"))
            if final:
                return final.replace("$NAME", path[0])

        return (success_path, record_type, path[0],
                'unable to find %s "%s" at namespace "%s"'
                % (record_type, path[0], url))
    
    else:
        ns_result = namespace["NS"].get(path[0])
        ns_loose = False
        if ns_result == None and "loose" in flags:
            ns_result = namespace["NS-loose"].get(pname)
            ns_loose = True
        
        pattern_result = namespace["PATTERN"].get(path[0])
        pattern_loose = False
        if pattern_result == None and "loose" in flags:
            pattern_result = namespace["PATTERN-loose"].get(pname)
            pattern_loose = True

        # precedence: NS, PATTERN, NS-loose, PATTERN-loose.

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
            try:
                pattern_result = pattern_result.replace("$NAME", path[1])
                for num in range(1, 10):
                    argkey = "$ARG%d" % num
                    if argkey in pattern_result:
                        pattern_result = pattern_result.replace(argkey, path[num])
            except IndexError:
                pass
            return pattern_result

        if use == "ns":
            success_path.append(path[0])
            return lookup(path[1:], ns_result, flags, success_path)

        return (success_path, "NS", path[0],
                'unable to find NS "%s" at namespace "%s"' % (path[0], url))


def _prepare_key(name):
    """
    Prepares a key for loose comparison.

    Returns the name in lower case, without any punctuation, white space,
    trailing "s", "int", "ed", or articles the, a, and an.
    
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
    Replace links, images, denoted by [[foo]] with A HREFs.

    text:  text to make replacements in
    namespace_url:  URL of namespace to start from
    softlink_base:  URL base to softlink from

    Examples:
        [[some name]]
        [[NS link][NS link][LN name]]
        [[some name]some other text covering it]
        [[NS link][LN name]some other text]
        [[:)]]

    Softlinks have the form:
      ((foo)(bar))
    ...which becomes a link to:
      (SOFTLINK_BASE)?action=redirect&url=(URL)&lookup=foo&lookup=bar

    Images (.png, .gif, .jpeg, .jpg) are made into
    <IMG SRC="http://..."/>, unless there is cover text,
    in which case it's linked text.  Only applies to
    hard lookups.
    """

    def replace_link(match):
        flags = sets.Set(["loose", "check-neighboring-spaces"])
        path = match.group(1)[1:-1].split('][')
        url = lookup(path, namespace_url, flags)
        if type(url) not in [type("string"), type(u'unicode')]:
            return '<font color="red">%s</a>' % url
        img = False
        for extension in image_extensions:
            if url.endswith(extension):
                img = True
        title = match.group(2)
        if title == None and not img:
            title = path[-1]
        if img and not title:
            return '<img src="%s"/>' % url
        return '<a href="%s">%s</a>' % (url, cgi.escape(title))

    def replace_softlink(match):
        flags = sets.Set(["loose", "check-neighboring-spaces"])
        path = match.group(1)[1:-1].split(')(')
        map = {'action': 'redirect', 'url': namespace_url, 'lookup': path}
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
    ns = aggregate(["http://taoriver.net/tmp/gmail.txt",
                    "http://ln.taoriver.net/localnames.txt"])
    print clean(ns)

