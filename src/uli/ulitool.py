"""
Command-line tool for interacting with ULI.

Recommended use:

  Write aliases to ulitool.

  ex:

  (TCSH:)

    alias uli "python2.3 ~/my/src/stage/onebigsoup/src/uli/ulitool.py"
  
    alias redir "uli http://localnames.taoriver.net/uli/"
    alias lst "uli http://services.taoriver.net:9303/"
    alias ln "uli -f xmlrpc http://services.taoriver.net:9090/"

  Then you can just type:

  ln "help"
  ln "list-spaces"
  ln "lion RoboticEvidence"
"""

import optparse
import sys

import uli

if __name__ == "__main__":
    usage = 'usage: %prog [-f xmlrpc] (URL) "string message to send to service"'
    parser = optparse.OptionParser(usage)
    parser.add_option( "-f", "--form", dest="form", default="http",
                       type="string", help = "http or xmlrpc" )
    (option, args) = parser.parse_args()
    if len(args) < 2:
        parser.error( "must specify URL of ULI service, and message to send" )
    if len(args) > 2:
        parser.error( "must write message to send within quotes" )
    (url,msg) = args

    func = { "http": uli.http, "xmlrpc": uli.xmlrpc }[ option.form ]
    print func( url, msg )
