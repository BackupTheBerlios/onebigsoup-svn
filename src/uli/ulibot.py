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

import ircbot, pickle, sys, uli

aliaslist = { }
debug = False

def ulibot(host, port, channels, nick, picklefile):
   p = ircbot.Bot(nick=nick, channels=channels)
   
   address_pattern = "(?:%s[:, ]+)" % p.nick
   
   def save():
      pickle.dump( aliaslist, open( picklefile, "w" ) )

   def f_hi(m, origin, (cmd, channel), text, p=p):
      p.msg(origin.sender, 'hi %s' % origin.nick)
   p.rule(f_hi, 'hi', r"(?i)^Hi %s(\!)?$" % p.nick)

   def f_uliAlias(m, origin, (cmd, channel), text, p=p):
      if debug: p.msg(origin.sender, 'alias accepted')
      name, form_name, target = m.group(1), m.group(2), m.group(3)
      form_func = uli.forms_by_name[form_name]
      aliaslist[name] = (form_func, target)
      save()
      p.msg(origin.sender, "added alias %r for %s to %s" % (name, uli.form_names[form_func], target))
   p.rule(f_uliAlias, 'alias',
          "^%s?alias ([^\s]+) ([^\s]+) (http://[^\s]+)$" % address_pattern)

   def f_uliListAliases(m,origin, (cmd, channel), text, p=p):
      p.msg(origin.sender, "the current list of bindings:")
      for binding in aliaslist:
         p.msg(origin.sender, "Alias: %s  Function: %s  Url: %s" %
               (binding,uli.form_names[aliaslist[binding][0]],
                aliaslist[binding][1]) )
   p.rule(f_uliListAliases, 'list-aliases', "^%s?list[- ]?aliases" % address_pattern)

   def f_uliAliasCommand(m, origin, (cmd, channel), text, p=p):
      alias = m.group(1)
      if aliaslist.has_key(alias):
         if debug: p.msg(origin.sender, "interpreting %s as an alias."
                         "sending %s as command..." % (alias,
                                                       m.group(2)))
         f_uliCommand(alias, m.group(2), origin)
   p.rule(f_uliAliasCommand, 'aliases', "^%s?([a-zA-Z]+) (.*)$" % address_pattern)

   def f_uliCommand(alias, command, origin):
      response = aliaslist[alias][0]( aliaslist[alias][1] , command )
      for line in response.splitlines():
         listoflines = f_chop_by_length( line , 400 )
         for littleline in listoflines:
            p.msg(origin.sender, littleline )

   def f_uliBotHelp(m, origin, (cmd, channel), text, p=p):
      p.msg(origin.sender, "Commands I understand:")
      p.msg(origin.sender, "list aliases, alias <form> <alias> <url>, "
            "<existing-alias> <command-string>, help, "
            "debug toggle, remove alias <alias>")
   p.rule(f_uliBotHelp, 'commands', "^%s(help|commands)$" % address_pattern)
   p.rule(f_uliBotHelp, 'commands', "^(help|commands) %s$" % p.nick)

   def f_uliBotDebugMode(m, origin, (cmd, channel), text, p=p):
      global debug
      debug = not debug
   p.rule(f_uliBotDebugMode, 'debug', "^%s?debug toggle" % address_pattern )

   def f_chop_by_length( longline, length):
      results = []
      while len(longline) > length:
         results.append( longline[:length] )
         longline = longline[length:]
      results.append(longline)
      return results

   def f_uliRemoveAlias(m, origin, (cmd, channel), text, p=p):
      alias = m.group(1)
      if aliaslist.has_key(alias):
         data = aliaslist[alias]
         del aliaslist[alias]
         p.msg(origin.sender, "removed alias %r whis was %s to %s" % (alias, uli.form_names[data[0]], data[1]))
         save()
      else:
         p.msg(origin.sender, "no such alias %r" % alias)
   p.rule(f_uliRemoveAlias, 'remove', "^%s?remove[- ]alias ([^\s]+)$" % address_pattern)

   p.run(host, port)

def main(args):
   global aliaslist
   if args:
      picklefile, nickname, ircserver = args[:3]
      rooms = args[3:]
   else:
      nickname = 'UliBot'
      ircserver = 'irc.freenode.net'
      rooms = ['#onebigsoup']
      picklefile = 'ulibot.p'
   try:
      aliaslist = pickle.load( open( picklefile ) )
   except IOError:
      pass
   ulibot(ircserver, 6667, rooms, nick=nickname, picklefile=picklefile)

if __name__=='__main__':
   main(sys.argv[1:])

