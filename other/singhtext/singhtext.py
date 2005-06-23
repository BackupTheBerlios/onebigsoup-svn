"""SinghText to HTML.

Headers:  == Heading 2 ==
Paragraphs:  Continuous text; Blank lines segregate paragraphs.
Bold and Italic:  '''bold''' ''italic''
Links:  [[http://example.com/]]  [[http://example.com/] link text]

Lists:  * first
        * second     -- starting in column 0
        ** nested    -- use # instead of * for an ordered list
        * outer

Further, there are *special lines* and *regions.*
* Special Lines: start with $foo, interpreted specially
* Regions: start with a #foo line, end with a repeat #foo line, and
           consist of the text between the two #foo lines.

This module uses native strings, and does nothing with encoding or
decoding to unicode.

tokenize_line  -- tokenize one line
tokenize_all  -- tokenize a complete text
text_to_paragraph  -- group TEXT lines into PARAGRAPHs
group_list_items  -- group ITEMs into LISTs.
join_by_pairs  -- place START and END markers in a list
html_escape  -- &entities;
bold_and_italics  -- '''bold''', ''italics''
hyperlink  -- [[links]] to <a hrefs>
treat  -- &entity;, '''bold''', ''italic'', and [[link]]
tokens_to_html  -- produce HTML lines
tokens_to_variables -- produce variables
tokens_to_names_list -- produce names list
digest_text  -- fully convert text to tokens
text_to_html  -- produce HTML
text_to_variables  -- collect variables from $set lines
text_to_names_list  -- collect names list from $name lines
"""

import re


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

# column 1:  token type
# column 2:  regular expression
tokenizing_checks = [
    ("HEADER", re.compile(r"^(=+)(.+)\1$")),
    ("*ITEM", re.compile(r"^(\*+)\s+(.+)$")),  # grouped: LIST
    ("#ITEM", re.compile(r"^(#+)\s+(.+)$")),  # grouped: LIST
    ("REGION-DELIMITER", re.compile(r"^(#\S+)\s*(.+)?$")),
    ("SPECIAL", re.compile(r"^(\$\S+)\s*(.+)?$")),
    ("BLANK", re.compile("^\s*$")),
    ("TEXT", re.compile(r"^(.+)$")),  # grouped: PARAGRAPH
    ]

link_regex = r"[[(.+?)](.*?)]"  # As we think it
link_regex = link_regex.replace("[", "\\[")  # [ isn't a character class
link_regex = link_regex.replace("]", "\\]")  # ] isn't a character class
link_re = re.compile(link_regex, re.DOTALL | re.MULTILINE)

special_set_re = re.compile("(\S+):\s*(.+)")  # $set (foo): (bar)


def tokenize_line(line, start_pos=0):
    """Tokenize one line of text.

    Returns a tuple of the form:
      (token_type, token_contents, start_pos, end_pos)

    tokenize_one reads tokenizing_checks for info about the token types.
    """
    end_pos = start_pos + len(line)
    for (token_type, regex) in tokenizing_checks:
        mo = regex.match(line)
        if mo is not None:
            return (token_type, mo.groups(),
                    start_pos, end_pos)
    # This should never happen.
    return ("ERROR", "can't figure out line type", start_pos, end_pos)


def tokenize_all(text):

    """Convert text into tokens.

    Return a list of tokens. The token format is described in the
    documentation string for function tokenize_line.
    
    TODO:
    * (./) write tokenize_line function
    * (./) update it's documentation
    * rework tokenize_all
    * update IT's documentation
    * erase tokenize_one
    * adjust the module documentation functions list
    QUESTION:
    * go to a line-based addressing system, instead of a token-based
      addressing system? (may have been a better decision to begin
      with...)
    """

    # Initialize the tokenizer.
    pos = 0
    results = []
    STATE_NORMAL = "normal"
    STATE_REGION = "inside a region"
    state = STATE_NORMAL

    # Initialize region processing variables.
    region_type = None  # ex: "#foo"
    region_data = None  # ex: "bar," in "#foo bar"
    region_lines = None
    region_start_pos = None

    # Read tokens.
    for line in text.splitlines():
        token = tokenize_line(line, pos)
        pos = token[3]  # End position
        
        if state == STATE_NORMAL:
            if token[0] != "REGION-DELIMITER":
                results.append(token)
            else:
                state = STATE_REGION
                region_type = token[1][0]
                region_data = token[1][1]
                region_lines = []
                region_start_pos = pos
        
        elif state == STATE_REGION:
            if token[0] != "REGION-DELIMITER" or \
               token[1][1] != region_data:
                region_lines.append(line + "\n")
            else:
                results.append(("REGION",
                                (region_type,
                                 region_data,
                                 "".join(region_lines)),
                                region_start_pos, pos))
                state = STATE_NORMAL
                region_type = None
                region_data = None
                region_lines = None
                region_start_pos = None
        
        pos = pos + 1  # Account for end of line character.
    
    return results


def text_to_paragraph(tokens):

    """Group TEXTs into PARAGRAPHs.
    
    PARAGRAPH has the form:
    ("PARAGRAPH", "all text contents", first_pos, last_pos)
    """
    
    result = []
    texts = []
    
    def seal_texts():
        if len(texts) == 0:
            return []
        contents = " ".join([x[1][0] for x in texts])
        first_pos = texts[0][2]
        last_pos = texts[-1][3]
        result.append(("PARAGRAPH", contents, first_pos, last_pos))
        return []
    
    for token in tokens:
        (token_type, token_contents, start_pos, end_pos) = token
        if token_type == "TEXT":
            texts.append(token)
        else:
            texts = seal_texts()
            result.append(token)

    texts = seal_texts()
    return result


def group_list_items(tokens):
    
    """Group *ITEMs and #ITEMs into LISTs.
    
    LIST has the form:
    ("LIST", [(level#, "*ITEM" or "#ITEM", "text"), ...],
     first_pos, last_pos)
    "
    """
    
    result = []
    list_items = []
    
    def seal_list():
        """Seal the current LIST token.
        list_items has the form:
        token, token, token, ...
        ...as described in tokenize_one's comment.
        """
        if len(list_items) == 0:
            return []
        contents = []
        for x in list_items:
            contents.append((len(x[1][0]), x[1][0][0], x[1][1]))
        first_pos = list_items[0][2]
        last_pos = list_items[-1][3]
        result.append(("LIST", contents, first_pos, last_pos))
        return []

    for token in tokens:
        (token_type, token_contents, start_pos, end_pos) = token
        if token_type in ["#ITEM", "*ITEM"]:
            list_items.append(token)
        elif token_type == "TEXT" and len(list_items) > 0:
            (old_type, old_contents,
             old_start_pos, old_end_pos) = list_items.pop()
            (old_list_type, old_text) = old_contents
            new_text = old_text + " " + token_contents[0]
            new_end_pos = end_pos
            new_token = (old_type, (old_list_type, new_text),
                         old_start_pos, new_end_pos)
            list_items.append(new_token)
        else:
            list_items = seal_list()
            result.append(token)

    list_items = seal_list()
    return result


def join_by_pairs(lst, start, end):
    """
    if   lst = [1,2,3,4,5,6,7,8],
    and  start = "a" and end = "b",
    
    result = [1,"a",2,"b",3,"a",4,"b",5,"a",6,"b",7,8]

    Notice that nothing is started that isn't ended.
    """
    num_links = len(lst)-1
    stops_lst = [start,end]*(num_links/2)
    result = []
    while len(stops_lst)>0:
        # add an item from  lst
        result.append(lst[0])
        lst = lst[1:]
        # add an item from  stops_lst
        result.append(stops_lst[0])
        stops_lst = stops_lst[1:]
    # copy over whatever is left
    result.extend(lst)
    return "".join(result)


def html_escape(text):
    """Produce entities within text.

    For example: & to &amp; < to &lt; > to &gt;
    """
    L = []
    for c in text:
        L.append(html_escape_table.get(c,c))
    return "".join(L)


def bold_and_italics(text):
    """Perform '''bold''' and ''italics'' replacements.

    Note that, this assumes you've already called html_escape.
    """
    L = text.split("&apos;&apos;&apos;")
    text = join_by_pairs(L, "<b>", "</b>")
    L = text.split("&apos;&apos;")
    text = join_by_pairs(L, "<i>", "</i>")
    return text


def hyperlink(text):

    """Turn links into <a href>'s."""

    all_links = link_re.findall(text)

    def make_ahref(matchobj):
        link_url, link_text = matchobj.groups()
        if link_text == "":
            link_text = link_url
        return '<a href="%s">%s</a>' % (link_url, link_text)
    
    text = link_re.sub(make_ahref, text)
    return text


def treat(text):
    """HTML escape, bold & italic, and link.

    This is a convenience function.
    """
    return hyperlink(bold_and_italics(html_escape(text)))


def tokens_to_html(tokens):
    """Read the list of tokens, and return a list of resulting HTML.

    The tokens should be fully digested. That is, list items should have
    been turned into lists, texts should have been grouped into
    paragraphs, all transformations should have been applied.
    """
    result = []
    for token in tokens:
        (token_type, token_contents, start_pos, end_pos) = token
        if token_type == "HEADER":
            (level, content) = token_contents
            level = len(level)
            result.append("<h%d>%s</h%d>" % (level, treat(content),
                                             level))
        elif token_type == "REGION":
            (region_type, region_data, content) = token_contents
            if region_type.upper() == "#CODE":
                content = html_escape(content)
                result.append("<p><code><pre>%s</pre></code></p>"
                              % content)
            elif region_type.upper() == "#LITERAL":
                result.append(content)
            else:
                result.append('<font color="red">')
                result.append('<p>Region "%s" not understood.</p>'
                              % region_type)
                result.append("<p><code><pre>%s</pre></code></p>"
                              % html_escape(content))
                result.append('</font>')
        elif token_type == "LIST":
            cur_level = 0
            list_stack = []
            token_contents = token_contents + [(0, "*", None)]
            for (level, list_type, text) in token_contents:
                list_type = {"*": "ul", "#": "ol"}[list_type]
                while cur_level < level:
                    result.append("<" + list_type + ">")
                    list_stack.append(list_type)
                    cur_level = cur_level + 1
                while cur_level > level:
                    result.append("</" + list_stack.pop() + ">")
                    cur_level = cur_level - 1
                if text is not None:
                    result.append("<li>" + treat(text) + "</li>")
        elif token_type == "SPECIAL":
            (dollar_text, content) = token_contents
            dollar_text = dollar_text.upper()
            if dollar_text == "$SET":
                pass
            elif dollar_text == "$NAME":
                result.append("<a name='%s'/>" % content)
            elif dollar_text == "$REM":
                pass
        elif token_type == "PARAGRAPH":
            result.append("<p>%s</p>" % treat(token_contents))
    return result


def tokens_to_variables(tokens):
    """Return dictionary and errors produced by $set lines.

    Returns data of the form:
      (dictionary,
       [(error-ID-string, error-info, error-info, ...),
        human-readable-error-string)]
    
    You can use this as soon as special lines have been identified in
    the tokens list.
    """
    variables_dictionary = {}
    errors = []
    for token in tokens:
        (token_type, token_contents, start_pos, end_pos) = token
        if token_type != "SPECIAL":
            continue
        (dollar_text, content) = token_contents
        dollar_text = dollar_text.upper()
        if dollar_text == "$SET":
            mo = special_set_re.match(content)
            if mo is None:
                errors.append(("BADSET", content))
                continue
            (key, val) = mo.groups()
            variables_dictionary[key] = val
    return (variables_dictionary, errors)


def tokens_to_names_list(tokens):
    """Return list of names produced by $name lines.

    Returns data of the form:
      ["name", "name", "name", ...]
    ... in the order that names appear in the text.

    You can use this as soon as special lines have been identified in
    the tokens list.
    """
    names = []
    for token in tokens:
        (token_type, token_contents, start_pos, end_pos) = token        
        if token_type != "SPECIAL":
            continue
        (dollar_text, content) = token_contents
        dollar_text = dollar_text.upper()
        if dollar_text == "$NAME":
            names.append(content)
    return names


def digest_text(text):
    """Fully convert text to final tokens list.

    Tokenize the text, and then apply all techniques for grouping and
    processing.
    """
    tokens = tokenize_all(text)
    tokens = group_list_items(tokens)
    tokens = text_to_paragraph(tokens)
    tokens = [x for x in tokens if x[0] != "BLANK"]
    return tokens


def text_to_html(text):
    """Fully convert text to HTML.

    This is a convenience function.
    """
    tokens = digest_text(text)
    return "\n".join(tokens_to_html(tokens))


def text_to_variables(text):
    """Fully convert text to variables.

    This is a convenience function.
    """
    tokens = tokenize_all(text)
    return tokens_to_variables(tokens)[0]


def text_to_names_list(text):
    """Read out names from text.

    This is a convenience function.
    """
    tokens = tokenize_all(text)
    return tokens_to_names_list(tokens)


if __name__ == "__main__":
    example = """
== Example ==

This is a paragraph made of multiple lines of text.
We're doing this so that we can later parse it together
into something we'll call a "paragraph," which can
contain '''bold''' and ''italic'' text, as well as
other stuff. Here's a [[Local Name]] for you,
as well as a traditional [[http://example.net/] link.]

Learn about Local Names: [[http://ln.taoriver.net/]]

#X
All of this text belongs
in region "X", as one token.

We use this for code blocks and stuff.
#X

Here's another paragraph. It's made of multiple lines,
and lies just after the dread "Region X." It has
features some tricky "entities" like <this> for HTML to
deal with.

* item 1
* item 2
** item 2-A
** item 2-B
** item 2-C
* item 3
* A paragraph of text.
This is made by just placing line after line after line
of text after the list item.

#CODE
<foo>
  <bar/>
  <baz/>
</foo>
#CODE
"""
    import pprint
    print "Going one by one:"
    print tokenize_one(example, 0)
    print tokenize_one(example, 1)
    print tokenize_one(example, 24)
    print tokenize_one(example, 25)
    print
    print "Going all at once:"
    pprint.pprint(tokenize_all(example))
    print
    print "The source text:"
    print example
    print
    print "Making PARAGRAPHs from TEXT:"
    print text_to_html(example)

    print digest_text("""
$set eggs: spam
$set foo: bar
""")

