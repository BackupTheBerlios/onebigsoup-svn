#!/usr/bin/python
"""Local Name Resolver File Parser."""

import re, urllib

r_token = re.compile(r'(?:"([^"\\]*(?:\\.[^"\\]*)*)")|(\S+)')

def parseMapping(line): 
   m = r_token.match(line)
   if not m: raise Exception, "Couldn't find token in %r." % line
   name, end = m.group(1) or m.group(2), m.end()
   uri = line[(end + 1):]
   return name, uri

class Parser(object): 
   def __init__(self, sink): 
      self.sink = sink
      self.file = None
      self.info = {}

   def feedFile(self, f): 
      self.file = f

   def feedFilename(self, fn): 
      self.file = open(fn, 'r')

   def feedURI(self, uri): 
      self.file = urllib.urlopen(uri)

   def feedString(self, s):
      import StringIO
      f = StringIO.StringIO(s)
      f.seek(0)
      self.file = f

   def feed(self, obj): 
      if hasattr(obj, 'readline'): 
         self.feedFile(obj)
      elif '\n' in obj or '\r' in obj: 
         self.feedString(obj)
      else: self.feedURI(obj)

   def parse(self): 
      while 1:
         line = self.file.readline()
         if not line: break
         if not line.strip(): continue

         key, value = line.split(' ', 1)
         value = value.rstrip('\r\n')

         {'Ignore': self.ignore, 
          'SubstitutionPattern': self.substitutionPattern, 
          'NamesList': self.namesList, 
          'Table': self.table, 
          'Connections': self.connections, 
          'KeyValue': self.keyValue, 
          'DefaultConnections': self.defaultConnections, 
          'DefaultPagePattern': self.defaultPagePattern}[key](value)

   def getBlock(self, key): 
      result = []
      end = '%s ENDS' % key
      while 1: 
         line = self.file.readline()
         line = line.rstrip('\r\n')
         if (not line) or (line == end): break
         if not line.strip(): continue
         result.append(line)
      return result

   def ignore(self, value): 
      if value == 'BEGINS': 
         for line in self.getBlock('Ignore'): 
            self.sink.comment(line)
      self.sink.comment(value)

   def substitutionPattern(self, value): 
      self.info['SubstitutionPattern'] = value

   def namesList(self, value): 
      sub = self.info.get('SubstitutionPattern')
      if sub is None: 
         raise ValueError, "No substitution pattern found for NamesList."

      if value == 'BEGINS': 
         for line in self.getBlock('NamesList'): 
            self.sink.map(line, sub.replace('$PAGE', line))
      else: 
         u = urllib.urlopen(value)
         while 1: 
            line = u.readline()
            line = line.rstrip('\r\n')
            if not line: break
            if not line.strip(): continue
            self.sink.map(line, sub.replace('$PAGE', line))
         u.close()

   def table(self, value): 
      if value == 'BEGINS': 
         for line in self.getBlock('Table'): 
            name, uri = parseMapping(line)
            self.sink.map(name, uri)
      else: 
         u = urllib.urlopen(value)
         while 1: 
            line = u.readline()
            line = line.rstrip('\r\n')
            if not line: break
            if not line.strip(): continue
            name, uri = parseMapping(line)
            self.sink.map(name, uri)
         u.close()

   def connections(self, value): 
      if value == 'BEGINS': 
         for line in self.getBlock('Connections'): 
            name, uri = parseMapping(line)
            self.sink.connection(name, uri)
      else: 
         u = urllib.urlopen(value)
         while 1: 
            line = u.readline()
            line = line.rstrip('\r\n')
            if not line: break
            if not line.strip(): continue
            name, uri = parseMapping(line)
            self.sink.connection(name, uri)
         u.close()

   def keyValue(self, value): 
      key, value = parseMapping(value)
      self.sink.meta(key, value)

   def defaultConnections(self, value): 
      if value == 'BEGINS': 
         for line in self.getBlock('DefaultConnections'): 
            self.sink.defaultConnection(line)
      else: 
         u = urllib.urlopen(value)
         while 1: 
            line = u.readline()
            line = line.rstrip('\r\n')
            if not line: break
            if not line.strip(): continue
            self.sink.defaultConnection(line)
         u.close()

   def defaultPagePattern(self, value): 
      self.sink.defaultPagePattern(value)

class TestSink(object): 
   """A Test Sink for the Parser class above."""

   def comment(self, s): 
      print 'COMMENT:', repr(s)

   def meta(self, key, value): 
      print 'META:', repr(key), repr(value)

   def map(self, name, uri): 
      print 'MAP:', repr(name), repr(uri)

   def connection(self, name, uri): 
      print 'CONNECTION:', repr(uri)

   def defaultConnection(self, name): 
      print 'DEFAULT CONNECTION:', repr(name)

   def defaultPagePattern(self, pattern): 
      print 'DEFAULT PAGE PATTERN:', repr(pattern)

def parseString(s, sink=None): 
   if sink is None: 
      sink = TestSink()
   p = Parser(sink)
   p.feedString(s)
   p.parse()
   return sink

def test(): 
   parseString("""
Ignore http://swhack.com/notes/LocalNamesSpecification
Ignore Hi, this is a generic comment.

SubstitutionPattern http://example.org/$PAGE
Ignore NamesList http://example.org/my-names-list

SubstitutionPattern http://example.org/more/$PAGE
NamesList BEGINS
FirstName
SecondName
NamesList ENDS

Table BEGINS
"World Wide Web Consortium" http://www.w3.org/
SomethingElse http://example.org/SomethingElse
Table ENDS

KeyValue "Page moving to" http://new.com/location/

Connections BEGINS
OneBigSoup http://onebigsoup.wiki.taoriver.net/LocalNamesSpec
CommunityWiki http://communitywiki.org/LocalNamesSpec
IntComm http://communitywiki.org/LocalNamesSpec
Connections ENDS

DefaultConnections BEGINS
IntComm
CommunityWiki
OneBigSoup
DefaultConnections ENDS

DefaultPagePattern http://swhack.com/notes/$PAGE
""")

if __name__=="__main__": 
   print __doc__
   test()
