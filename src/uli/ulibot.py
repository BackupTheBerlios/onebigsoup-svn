#!/usr/bin/python
"""
UliBot - A Basic Uli-Oriented IRC Bot
License: GPL 2; share and enjoy!
Authors:
Sean B. Palmer, inamidst.com
   Suw Charman, chocnvodka.blogware.com
Augmented by:
   Dave Menninger
Requirements:
   http://inamidst.com/proj/suwbot/ircbot.py
"""

import ircbot, urllib, xmlrpclib, pickle, sys

nickname = 'UliBot'
ircserver = 'irc.freenode.net'
room = '#onebigsoup'
picklefile = 'ulibot.p'

aliaslist = { }
debug = False

def http( url, line ):
   # urllib.urlopen ignores HTTP errors and doesn't tell us about them
   uo = urllib.URLopener()
   response = uo.open( url, urllib.urlencode( {"ULI":line} ) )
   ctype = response.info()["Content-Type"]
   if ctype == "text/plain":
      return response.read()
   else:
      raise IOError, "Wrong Content-Type for ULI response: %s" % ctype

def xmlrpc( url, line ):
   return xmlrpclib.ServerProxy( url ).uli( line )

def prompt( prompt_string, uli_url, call_func ):
   """
   prompt_string: ex: "<uli-9095> "
   uli_url:       ex: "http://services.taoriver.net:9095/"
   call_func:     uli.http or uli.xmlrpc
   """
   input = ""
   while input.upper() != "QUIT":
       input = raw_input( prompt_string )
       if input.upper() != "QUIT":
           print call_func( uli_url, input )

funcnames = { http: "http", xmlrpc: "xml-rpc"}

def ulibot(host, port, channels, nick=nickname):
   p = ircbot.Bot(nick=nick, channels=channels)

   def f_hi(m, origin, (cmd, channel), text, p=p):
      p.msg(origin.sender, 'hi %s' % origin.nick)
   p.rule(f_hi, 'hi', r"(?i)^Hi %s(\!)?$" % p.nick)

   def f_uliHTTPalias(m, origin, (cmd, channel), text, p=p):
      if debug: p.msg(origin.sender, 'alias accepted')
      allsplitup = text.split()
      aliaslist[allsplitup[1]] = (http, allsplitup[2])
      pickle.dump( aliaslist, open( picklefile, "w" ) )
   p.rule(f_uliHTTPalias, 'ulihttpalias',
          "uli-http [a-zA-Z]+ http://.+$" )

   def f_uliXMLRPCalias(m, origin, (cmd, channel), text, p=p):
      if debug: p.msg(origin.sender, 'alias accepted')
      allsplitup = text.split()
      aliaslist[allsplitup[1]] = (xmlrpc, allsplitup[2])
      pickle.dump( aliaslist, open( picklefile, "w" ) )
   p.rule(f_uliXMLRPCalias, 'ulixmlrpcalias',
          "uli-xmlrpc [a-zA-Z]+ http://.+$" )

   def f_uliListAliases(m,origin, (cmd, channel), text, p=p):
      p.msg(origin.sender, "the current list of bindings:")
      for binding in aliaslist:
         p.msg(origin.sender, "Alias: %s  Function: %s  Url: %s" %
               (binding,funcnames[aliaslist[binding][0]],
                aliaslist[binding][1]) )
   p.rule(f_uliListAliases, 'ulilistaliases', "uli-list-aliases")

   def f_uliAliasCommand(m, origin, (cmd, channel), text, p=p):
      allsplitup = text.split(None,1)
      alias = allsplitup[0]
      if aliaslist.has_key(alias):
         if debug: p.msg(origin.sender, "interpreting %s as an alias."
                         "sending %s as command..." % (alias,
                                                       allsplitup[1]))
         f_uliCommand(alias, allsplitup[1], origin)
   p.rule(f_uliAliasCommand, 'ulialiascommand', "[a-zA-Z]+ ([a-zA-Z]+)*" )

   def f_uliCommand(alias, command, origin):
      response = aliaslist[alias][0]( aliaslist[alias][1] , command )
      for line in response.splitlines():
         listoflines = f_chop_by_length( line , 80 )
         for littleline in listoflines:
            p.msg(origin.sender, littleline )

   def f_uliBotHelp(m, origin, (cmd, channel), text, p=p):
      p.msg(origin.sender, "Commands I understand:")
      p.msg(origin.sender, "uli-list-aliases, uli-http <alias> <url>, "
            "uli-xmlrpc <alias> <url>, <existing-alias> <command-string>, help %s, "
            "debug toggle %s, remove alias <alias>" % (p.nick,p.nick))
   p.rule(f_uliBotHelp, 'ulibothelp', "help %s" % p.nick )

   def f_uliBotDebugMode(m, origin, (cmd, channel), text, p=p):
      global debug
      debug = not debug
   p.rule(f_uliBotDebugMode, 'ulibotdebugmode', "debug toggle %s" % p.nick )

   def f_chop_by_length( longline, length):
      results = []
      while len(longline) > length:
         results.append( longline[:length] )
         longline = longline[length:]
      results.append(longline)
      return results

   def f_uliRemoveAlias(m, origin, (cmd, channel), text, p=p):
      allsplitup = text.split(" ")
      alias = allsplitup[2]
      if aliaslist.has_key(alias):
         del aliaslist[alias]
   p.rule(f_uliRemoveAlias, 'uliremovealias', "remove alias [a-zA-Z]+" )

   p.run(host, port)

def main(args):
   global aliaslist
   try:
      aliaslist = pickle.load( open( picklefile ) )
   except IOError:
      pass
   ulibot(ircserver, 6667, [room])

if __name__=='__main__':
   main(sys.argv[1:])

