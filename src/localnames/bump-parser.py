#!/usr/bin/python

import re

r_bump = re.compile(r'((?:[A-Z][a-z]+){2,})')
r_bumps = re.compile(r'((?:(?:[A-Z][a-z]+){2,}:)*(?:[A-Z][a-z]+){2,})')

def parseName(input): 
   pos = 0
   result = []
   while 1:
      m = r_bump.match(input[pos:])
      if m:
         result.append(m.group(1))
         pos += m.end()
         if pos < len(input):
            assert input[pos:].startswith(':')
            pos += 1
         else: break
   return tuple(result)

def parseString(s): 
   pos, spans = 0, [0]

   while 1: 
      m = r_bumps.search(s, pos)
      if not m: break
      pos = m.end()
      word = m.group(0)
      spans.extend(m.span())
   spans.append(len(s))

   result = []
   for i, span in enumerate(spans): 
      if (i + 1) > (len(spans) - 1): break
      if not (i % 2): result.append(s[span:spans[i+1]])
      else: result.append(parseName(s[span:spans[i+1]]))

   return result

def main(): 
   test = "This is a string with BumpyCase and IntComm:OtherStuff ..."
   print parseString(test)

if __name__=="__main__": 
   main()
