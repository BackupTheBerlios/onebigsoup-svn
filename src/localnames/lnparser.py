#!/usr/bin/python
"""
Local Names Namespace File Parser

1. Read file
2. Sanitize to [(#spaces indent,string)]
3. Go through list, processing what isn't a comment.
"""

import urllib,re

LEADING_URL = "http://purl.net/net/onebigsoup/localnames/"


r_token = re.compile(r'(?:"([^"\\]*(?:\\.[^"\\]*)*)")|(\S+)')

def parseMapping(line):
    m = r_token.match(line)
    if not m: raise Exception, "Couldn't find token in %r." % line
    name, end = m.group(1) or m.group(2), m.end()
    uri = line[(end + 1):]
    return name, uri


class Parser:
    def __init__( s, sink ):
        s.sink = sink
        s.lines = None
        s.indent = None
        s.names_list_pattern = None

    def feedFile( s, f ):
        s.sanitizeLines( f.readlines() )
    def feedFilename( s, fn ):
        s.sanitizeLines( file(fn,"r").readlines() )
    def feedUrl( s, url ):
        s.sanitizeLines( urllib.urlopen(uri).readlines() )
    def feedString( s, a_string ):
        s.sanitizeLines( a_string.split("\n") )
    def sanitizeLines( s, lines ):
        def count_spaces( x ):
            if len(x)>0 and x[0]==" ":
                return 1+count_spaces(x[1:])
            return 0
        linenumbers = iter(range(1,len(lines)+1))
        s.lines = [ (linenumbers.next(), # line-number (starting from 1)
                     count_spaces(line), # number of spaces at front
                     line.strip()) for line in lines ] # stripped contents
    
    def parse(s):
        while 1:
            if len(s.lines)==0:raise "Leading URL %s not found alone in document." % LEADING_URL
            (line_number,spaces,line) = s.lines.pop(0)
            if line == LEADING_URL:
                s.indent = spaces
                break

        while 1:
            if len(s.lines)==0:break
            (linenum,spaces,line) = s.lines.pop(0)
            if spaces == 0:
                continue # comment line
            if spaces != s.indent:
                raise "Indentation on line %d should be %d spaces, presently %d spaces." % (linenum,s.indent,spaces)

            linedata = line.split(' ', 1)
            if len(linedata)==1: (key,value) = linedata[0],""
            if len(linedata)==2: (key,value) = linedata
            value=value.strip()
            
            {'NamesListPattern': s.namesListPattern,
             'NamesList': s.namesList,
             'NamesTable': s.namesTable,
             'OtherNameSpaces': s.otherNameSpaces,
             'KeyValue': s.keyValue,
             'DefaultNameSpaces': s.defaultNameSpaces,
             'LastResortNamePattern': s.lastResortNamePattern}[key](value)
    
    def getBlock(s):
        result=[]
        while 1:
            if len(s.lines)==0: return result # EOF
            (linenum,spaces,line) = whole = s.lines.pop(0)
            if spaces == 0: continue # comment
            if spaces == s.indent:         # out of block:
                s.lines.insert( 0, whole ) # |-> so revert
                return result              # |-> and return
            if spaces != s.indent*2:
                raise "Indentation on line %d should be %d spaces, presently %d spaces." % (linenum,s.indent*2,spaces)
            result.append( parseMapping(line) )

    def namesListPattern(s, value):
        s.names_list_pattern = value

    def namesList(s, value):
        if s.names_list_pattern is None:
            raise ValueError, "No substitution pattern found for NamesList."

        if value == "":
            for row in s.getBlock():
                name,dummy = row
                s.sink.map( name, s.names_list_pattern.replace("$NAME",name) )
        else:
            u = urllib.urlopen(value)
            while 1:
                line = u.readline()
                line = line.rstrip('\r\n')
                if not line: break
                if not line.strip(): continue
                s.sink.map(line, s.names_list_pattern.replace('$NAME', line))
            u.close()

    def namesTable(s, value):
        old_uri = None
        if value == '':
            for row in s.getBlock():
                name,uri = row
                if row[1] == "":uri=old_uri
                s.sink.map( name,uri)
                old_uri=uri
        else:
            u = urllib.urlopen(value)
            while 1: 
                line = u.readline()
                line = line.rstrip('\r\n')
                if not line: break
                if not line.strip(): continue
                name, uri = parseMapping(line)
                s.sink.map(name, uri)
            u.close()

    def otherNameSpaces(s, value):
        old_uri = None
        if value == '':
            for row in s.getBlock():
                name, uri = row
                if uri == "": uri=old_uri
                s.sink.otherNameSpace(name, uri)
                old_uri = uri
        else:
            u = urllib.urlopen(value)
            while 1: 
                line = u.readline()
                line = line.rstrip('\r\n')
                if not line: break
                if not line.strip(): continue
                name, uri = parseMapping(line)
                s.sink.otherNameSpace(name, uri)
            u.close()

    def keyValue( s, value ):
        key, value = parseMapping( value )
        s.sink.meta(key,value)

    def defaultNameSpaces( s, value ):
        if value == '':
            for line in s.getBlock():
                s.sink.defaultNameSpaces(line)
        else:
            u = urllib.urlopen(value)
            while 1: 
                line = u.readline()
                line = line.rstrip('\r\n')
                if not line: break
                if not line.strip(): continue
                s.sink.defaultNameSpaces(line)
            u.close()

    def lastResortNamePattern( s, value ):
        s.sink.lastResortNamePattern( value )

class TestSink(object): 
   """A Test Sink for the Parser class above."""

   def meta(self, key, value): 
      print 'META:', repr(key), repr(value)

   def map(self, name, uri): 
      print 'MAP:', repr(name), repr(uri)

   def otherNameSpace(self, name, uri): 
      print 'OTHER NAME SPACE:', repr(uri)

   def defaultNameSpaces(self, name): 
      print 'DEFAULT NAME SPACE:', repr(name)

   def lastResortNamePattern(self, pattern): 
      print 'LAST RESORT NAME PATTERN:', repr(pattern)

def parseString(s, sink=None): 
   if sink is None: 
      sink = TestSink()
   p = Parser(sink)
   p.feedString(s)
   p.parse()
   return sink

def test1(): 
   parseString("""
This is a Local Names namespace spec for describing Marshall Brain's sites that I find interesting.

For more information, see:

  http://purl.net/net/onebigsoup/localnames/

General Robotics interest:

  NamesTable
    "Robotic Nation" http://www.marshallbrain.com/robotic-nation.htm
    RoboticNation
    "Robots in 2015" http://marshallbrain.com/robots-in-2015.htm
    RobotsIn2015
    "Robotic Freedom" http://marshallbrain.com/robotic-freedom.htm
    RoboticFreedom
    "Robotic Nation FAQ" http://marshallbrain.com/robotic-faq.htm
    RoboticNationFAQ
    RoboticNationFaq
    "Robotic Nation Evidence" http://roboticnation.blogspot.com/
    RoboticNationEvidence
    Evidence

    Manna http://www.marshallbrain.com/manna1.htm

Other stuff:

    "How Stuff Works" http://www.howstuffworks.com/
    HowStuffWorks
    HowThingsWork

  OtherNameSpaces

So far, only one.

    "Robotics Wiki" http://www-robotics.usc.edu/~dshell/roboticswiki/index.php/LocalNamesDescription
    RoboticsWiki
    Robotics

And miscellaneous information...

  NamesTable
    NamespaceLocation http://taoriver.net/lns/marshall-brain.txt
    NamespaceAuthor   http://purl.net/net/lions/homepage/

And some meta-data:

  KeyValue Author     "Lion Kimbro"
  KeyValue AuthorURL  http://purl.net/net/lions/homepage/
  KeyValue AuthorFOAF http://purl.net/net/lions/foaf/

Enjoy!
""")

def test2(): 
   parseString("""
Lion Kimbro's favorites.

   http://purl.net/net/onebigsoup/localnames/

   NamesListPattern http://www.speakeasy.org/~lion/$NAME/$NAME/
   NamesList
      Foo
      Bar
      Baz

   OtherNameSpaces
      MarshallBrain http://taoriver.net/lns/marshall-brain.txt

   NamesTable
      NamespaceAuthor http://purl.net/net/lions/homepage/

   KeyValue Author     "Lion Kimbro"
   KeyValue AuthorURL  http://purl.net/net/lions/homepage/
   KeyValue AuthorFOAF http://purl.net/net/lions/foaf/
""")

def test3():
    parseString("""
Testing a wiki's names space

     http://purl.net/net/onebigsoup/localnames/

     NamesListPattern http://onebigsoup.wiki.taoriver.net/moin.cgi/$NAME
     NamesList http://onebigsoup.wiki.taoriver.net/moin.cgi/TitleIndex?action=titleindex
""")

if __name__=="__main__": 
   print __doc__
   test1()
   print "----------------"
   test2()
   print "----------------"
   test3()
