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

  /!\ Special Lines, Regions, Only partially supported! /!\


tokenize_one  -- tokenize one line
tokenize_all  -- tokenize a complete text
text_to_paragraph  -- group TEXT lines into PARAGRAPHs
group_list_items  -- group ITEMs into LISTs.
join_by_pairs  -- place START and END markers in a list
bold_and_italics  -- '''bold''', ''italics''
hyperlink  -- resolve all links
tokens_to_html  -- produce HTML lines
text_to_html  -- produce HTML
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
    ("HEADER", re.compile(r"(=+)(.+?)\1\n")),
    ("*ITEM", re.compile(r"(\*+) (.+?)\n")),  # grouped: LIST
    ("#ITEM", re.compile(r"(#+) (.+?)\n")),  # grouped: LIST
    ("BLANK", re.compile(r"(\s*?)\n")),
    ("REGION", re.compile(r"#(.+?)\n((?:.*?\n)+?)#\1\n")),
    ("TEXT", re.compile(r"(.+?\n)")),  # Last resort, grouped: PARAGRAPH
    ]

link_regex = r"[[(.+?)](.*?)]"  # As we think it
link_regex = link_regex.replace("[", "\\[")  # [ isn't a character class
link_regex = link_regex.replace("]", "\\]")  # ] isn't a character class
link_re = re.compile(link_regex)

special_line_handlers = {
    }


def tokenize_one(text, pos):
    """Read a token from the text, starting from a given position.

    Returns a tuple of the form:
      (token_type, token_contents, start_pos, end_pos)

    The end_pos is the next token's start_pos. That is,
    str[start_pos:end_pos] gives you the text consumed by the tokenizer.

    tokenize_one reads tokenizing_checks for info about the token types.
    """
    for (token_type, regex) in tokenizing_checks:
        mo = regex.match(text[pos:])
        if mo is not None:
            return (token_type, mo.groups(),
                    pos, pos+mo.end())
    # This should never happen.
    return ("ERROR", "can't figure out line type", pos, newline_pos)


def tokenize_all(text):
    if text[-1] != "\n":
        text = text + "\n"
    pos = 0
    results = []
    error = False
    while pos < len(text) and not error:
        result = tokenize_one(text, pos)
        results.append(result)
        (token_type, token_contents, start_pos, end_pos) = result
        error = token_type == "ERROR"
        pos = end_pos
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
        contents = "".join([x[1][0] for x in texts])
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
    """Produce entities within text."""
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


def tokens_to_html(tokens):
    """Read the list of tokens, and return a list of resulting HTML.

    The tokens should be fully digested. That is, all the grouping and transformation functions should have been applied.
    """
    result = []
    for token in tokens:
        (token_type, token_contents, start_pos, end_pos) = token
        if token_type == "HEADER":
            (level, content) = token_contents
            level = len(level)
            result.append("<h%d>%s</h%d>" % (level, content, level))
        elif token_type == "REGION":
            (region_type, content) = token_contents
            if region_type.upper() == "CODE":
                content = html_escape(content)
                result.append("<p><code><pre>%s</pre></code></p>"
                              % content)
            elif region_type.upper() == "LITERAL":
                result.append(content)
            else:
                result.append('<font color="red">')
                result.append('Region "%s" not understood.'
                              % region_type)
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
                    result.append("<li>" + text + "</li>")
        elif token_type == "PARAGRAPH":
            text = html_escape(token_contents)
            text = bold_and_italics(text)
            text = hyperlink(text)
            result.append("<p>%s</p>" % text)
    return result


def text_to_html(text):
    """Fully convert text to HTML."""
    tokens = tokenize_all(text)
    tokens = group_list_items(tokens)
    tokens = text_to_paragraph(tokens)
    tokens = [x for x in tokens if x[0] != "BLANK"]
    return "\n".join(tokens_to_html(tokens))


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

