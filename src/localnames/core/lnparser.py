#!/usr/bin/python
"""
Local Names Namespace File Parser

1. Read file
2. Sanitize to [(line_number,three_tokens)...]
3. Go through list, reporting to data sink
"""

import re
import urllib

# white space
optional_ws = "\s*"
ws = "\s+"

token_without_ws = '\S+' # blah
quoted_token = '"[^"]+"' # " blah  blah blah  "

token = "("+quoted_token+"|"+token_without_ws+")" # check quoted_token 1st
record = "^"+optional_ws+token+ws+token+ws+token+optional_ws+"$"

# end result is:
#
#    ^\s+?("[^"]+"|\S+)\s+("[^"]+"|\S+)\s+("[^"]+"|\S+)\s+?$

tokenizer = re.compile( record )


class Parser:
    def __init__( s, sink ):
        s.sink = sink
        s.lines = None
        s.feed_name = "(feedname)"

    def sanitizeLines( s, lines ):
        """
        
        Accepts a list of lines, cuts the list of lines into
        lists of lists of tokens, and remembers the line #.

        ex:
            ['''This is "a list" "of lines"\n''',
             '''\n''',
             '''\n''',
             '''Foo Bar\n''',]

        becomes:
            [ (1,["This","is","a list","of lines"]),
              (4,["Foo","Bar"]) ]
              
        """
        result = []
        
        for (i,x) in enumerate( lines ):
            if x.strip() != "" and x[0] != "#":
                try:
                    xmatch = list( tokenizer.match( x ).groups() )
                    for (i,elem) in enumerate(xmatch):
                        if elem[0]=='"' and elem[-1]=='"':
                            elem = elem[1:-1] # de-quote the ends
                            xmatch[i] = elem
                    result.append( (i+1,xmatch) )
                except AttributeError:
                    s.sink.warning( i+1, "line improperly formatted" )
        return result
    def feedFile( s, f ):
        s.feed_name = "(some file)"
        s.lines = s.sanitizeLines( f.readlines() )
    def feedFilename( s, fn ):
        s.feed_name = "(file: %s)" % fn
        s.lines = s.sanitizeLines( file(fn,"r").readlines() )
    def feedUrl( s, url ):
        s.feed_name = "(url: %s)" % url
        s.lines = s.sanitizeLines( urllib.urlopen(url).readlines() )
    def feedString( s, a_string ):
        s.feed_name = "(some string)"
        s.lines = s.sanitizeLines( a_string.split("\n") )
    
    def parse(s):
        """
        Go through each line of data, and invoke the sink appropriately.

        The Sink interface is this:
        * LN( name, uri ) -- for local names
        * NS( name, uri ) -- for namespaces
        * X( key, value ) -- for extensions
        * FINAL( pattern ) -- for last resort URL, with "$NAME" substitution
        * warning( line_number, message ) -- for warnings, errors
        """
        last = (None,None,None)
        
        for (line_number,line_data) in s.lines:
            if len( line_data ) != 3:
                s.sink.warning( line_number, "3 tokens required" )
                continue
            
            for index in range(3):
                if line_data[ index ] == ".":
                    line_data[ index ] = last[ index ]
            (record_type, key, val ) = line_data

            if record_type not in [ "LN", "NS", "X", "FINAL" ]:
                s.sink.warning( line_number, "must be a LN, NS, X, or FINAL record" )
                continue

            last = line_data

            if record_type == "LN":
                s.sink.LN( key, val )
            elif record_type == "NS":
                s.sink.NS( key, val )
            elif record_type == "X":
                s.sink.X( key, val )
            elif record_type == "FINAL":
                s.sink.FINAL( key )

class TestSink(object): 
   """A Test Sink for the Parser class above."""

   def LN(s, name, uri ): 
       print 'LN:', name, uri

   def NS(s, name, uri ):
       print 'NS:', name, uri

   def X(s, key, val ):
       print "X:", key, val

   def FINAL(s, pattern ):
       print "FINAL:", pattern

   def warning(s, line_number, msg ):
       print 'WARNING (%d): %s' % (line_number, msg)

def parseString(s, sink=None): 
   if sink is None: 
      sink = TestSink()
   p = Parser(sink)
   p.feedString(s)
   p.parse()
   return sink

def test1(): 
   parseString("""
# This is a Local Names namespace spec for
# describing Marshall Brain's sites that
# I find interesting.

# For more information, see:
#   http://purl.net/net/localnames/

# General Robotics interest:
LN  "Robotic Nation" http://www.marshallbrain.com/robotic-nation.htm
LN  RoboticNation .
LN  "Robots in 2015" http://marshallbrain.com/robots-in-2015.htm
LN  RobotsIn2015 .
LN  "Robotic Freedom" http://marshallbrain.com/robotic-freedom.htm
LN  RoboticFreedom .
LN  "Robotic Nation FAQ" http://marshallbrain.com/robotic-faq.htm
LN  RoboticNationFAQ .
LN  RoboticNationFaq .
LN  "Robotic Nation Evidence" http://roboticnation.blogspot.com/
LN  RoboticNationEvidence .
LN  Evidence .

LN  Manna http://www.marshallbrain.com/manna1.htm

# Other stuff:

LN "Intentionally buggy - look, no final quotation mark! http://blahblah/

LN  "How Stuff Works" http://www.howstuffworks.com/
LN  HowStuffWorks .
LN  HowThingsWork .

NS  "Robotics Wiki" http://www-robotics.usc.edu/~dshell/roboticswiki/index.php/LocalNamesDescription
NS  RoboticsWiki .
NS  Robotics .

LN  NamespaceLocation http://taoriver.net/lns/marshall-brain.txt
LN  NamespaceAuthor   http://purl.net/net/lions/homepage/

# And some meta-data:

X  Author     "Lion Kimbro"
X  AuthorURL  http://purl.net/net/lions/homepage/
X  AuthorFOAF http://purl.net/net/lions/foaf/

# Enjoy!
""")

if __name__=="__main__": 
   print __doc__
   test1()

