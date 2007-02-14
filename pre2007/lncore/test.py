"""DOC

DOC

DOC
"""

import unittest

import lncore


basic_text = u"""
X "VERSION" "1.2"
LN "foo" "http://example.com/"
LN "bar" "http://example.com/"
X "FINAL" "http://example.com/$NAME"
NS "neighbor" "http://example.net/"
PATTERN "pat" "http://example.com/$ARG1/$ARG2/"
"""

'''Basic namespace description for use in simple tests.'''

neighbor_text = u"""
X "VERSION" "1.2"
LN "baz boz" "http://example.net/bazboz/"
"""

'''Neighbor namespace description for testing namespace links.'''

pythoninfo_text = u"""
# {{{
#
#   Aren't URLs tedius? Have you ever wished you could just say the
#   name of a web page, and get right to it? Here's something you can
#   use to jump to any page in the Python Library Reference, by name,
#   or any page of this wiki.
#
#
#   Make a special bookmark in Firefox to do this:
#
#   1.  Under "Bookmarks," pick "Manage Bookmarks"
#
#   2.  Create a new bookmark, call it "Python Reference,"
#       and set the Location to:
#
#             "http://localnames.taoriver.net/pythonref/%s"
#
#       Set the keyword to "python".
#
#   3.  Put the bookmark in the "Quick Searches" folder.
#
#
# Now, at the address bar, you can just type something like:
#
#         python cgi
#
# ...and you'll be at the Python Reference CGI page.
#
# Or type something like:
#
#         python FrontPage
#
# ...and you'll be at the front page of the wiki.
#
# Take care!
#
#
# (If you're curious how this works, it's all just a bunch
#  of webservices and browser redirection.)
#
# ( You can pull down the namespace binding with the following
#   code, if you like, as well:
#
#   import xmlrpclib
#   nameserver = xmlrpclib.ServerProxy( "http://services.taoriver.net:9089/" )
#   nameserver.parse_description( "http://wrap.localnames.taoriver.net/spaces/pythoninfo/" )
#
#   You'll get back a big fat dictionary of name-URL bindings.
#   See http://services.taoriver.net:9089/ for other functionality available to you. )
#

LN "this" "http://www.python.org/moin/LibraryReferencesNames?action=raw"
LN "edit" "http://www.python.org/moin/LibraryReferencesNames?action=edit"
LN "LibraryReference" "http://www.python.org/doc/current/lib/"

# Some things from the beginning of the Library Reference:

LN "BuiltInObjects" "http://www.python.org/doc/current/lib/builtin.html"
LN "BuiltInFunctions" "http://www.python.org/doc/current/lib/built-in-funcs.html"
LN "NonEssentialBuiltInFunctions" "http://www.python.org/doc/current/lib/non-essential-built-in-funcs.html"
LN "BuiltInTypes" "http://www.python.org/doc/current/lib/types.html"
LN "TruthValueTesting" "http://www.python.org/doc/current/lib/truth.html"
LN "BooleanOperations" "http://www.python.org/doc/current/lib/boolean.html"
LN "Comparisons" "http://www.python.org/doc/current/lib/comparisons.html"
LN "NumericTypes" "http://www.python.org/doc/current/lib/typesnumeric.html"
LN "IteratorTypes" "http://www.python.org/doc/current/lib/typeiter.html"
LN "SequenceTypes" "http://www.python.org/doc/current/lib/typesseq.html"
LN "MappingTypes" "http://www.python.org/doc/current/lib/typesmapping.html"
LN "FileObjects" "http://www.python.org/doc/current/lib/bltin-file-objects.html"
LN "OtherBuiltInTypes" "http://www.python.org/doc/current/lib/typesother.html"
LN "SpecialAttributes" "http://www.python.org/doc/current/lib/specialattrs.html"
LN "BuiltInExceptions" "http://www.python.org/doc/current/lib/module-exceptions.html"
LN "BuiltInConstants" "http://www.python.org/doc/current/lib/node34.html"

# Most Modules.
#
# Warning: The remainder of the listing was made by a crude process;
# Some entries may be missing. Feel free to edit and fix.
#
# Also feel free to add additional aliases, like how "copy_reg" is also just "copyreg".

LN "PythonRuntimeServices" "http://www.python.org/doc/current/lib/python.html"
LN "sys" "http://www.python.org/doc/current/lib/module-sys.html"
LN "gc" "http://www.python.org/doc/current/lib/module-gc.html"
LN "weakref" "http://www.python.org/doc/current/lib/module-weakref.html"
LN "fpectl" "http://www.python.org/doc/current/lib/module-fpectl.html"
LN "atexit" "http://www.python.org/doc/current/lib/module-atexit.html"
LN "types" "http://www.python.org/doc/current/lib/module-types.html"
LN "UserDict" "http://www.python.org/doc/current/lib/module-UserDict.html"
LN "UserList" "http://www.python.org/doc/current/lib/module-UserList.html"
LN "UserString" "http://www.python.org/doc/current/lib/module-UserString.html"
LN "operator" "http://www.python.org/doc/current/lib/module-operator.html"
LN "inspect" "http://www.python.org/doc/current/lib/module-inspect.html"
LN "traceback" "http://www.python.org/doc/current/lib/module-traceback.html"
LN "linecache" "http://www.python.org/doc/current/lib/module-linecache.html"
LN "pickle" "http://www.python.org/doc/current/lib/module-pickle.html"
LN "cPickle" "http://www.python.org/doc/current/lib/module-cPickle.html"
LN "copy_reg" "http://www.python.org/doc/current/lib/module-copyreg.html"
LN "copyreg" .
LN "shelve" "http://www.python.org/doc/current/lib/module-shelve.html"
LN "copy" "http://www.python.org/doc/current/lib/module-copy.html"
LN "marshall" "http://www.python.org/doc/current/lib/module-marshal.html"
LN "marshal" .
LN "warnings" "http://www.python.org/doc/current/lib/module-warnings.html"
LN "imp" "http://www.python.org/doc/current/lib/module-imp.html"
LN "pkgutil" "http://www.python.org/doc/current/lib/module-pkgutil.html"
LN "code" "http://www.python.org/doc/current/lib/module-code.html"
LN "codeop" "http://www.python.org/doc/current/lib/module-codeop.html"
LN "pprint" "http://www.python.org/doc/current/lib/module-pprint.html"
LN "repr" "http://www.python.org/doc/current/lib/module-repr.html"
LN "new" "http://www.python.org/doc/current/lib/module-new.html"
LN "site" "http://www.python.org/doc/current/lib/module-site.html"
LN "user" "http://www.python.org/doc/current/lib/module-user.html"
LN "__builtin__" "http://www.python.org/doc/current/lib/module-builtin.html"
.  "builtin" .
LN "__main__" "http://www.python.org/doc/current/lib/module-main.html"
.  "main" .
LN "__future__" "http://www.python.org/doc/current/lib/module-future.html"
.  "future" .
LN "string" "http://www.python.org/doc/current/lib/module-string.html"
LN "re" "http://www.python.org/doc/current/lib/module-re.html"
LN "struct" "http://www.python.org/doc/current/lib/module-struct.html"
LN "difflib" "http://www.python.org/doc/current/lib/module-difflib.html"
LN "fpformat" "http://www.python.org/doc/current/lib/module-fpformat.html"
LN "StringIO" "http://www.python.org/doc/current/lib/module-StringIO.html"
LN "cStringIO" "http://www.python.org/doc/current/lib/module-cStringIO.html"
LN "textwrap" "http://www.python.org/doc/current/lib/module-textwrap.html"
LN "codecs" "http://www.python.org/doc/current/lib/module-codecs.html"
LN "encodings.idna" "http://www.python.org/doc/current/lib/module-encodings.idna.html"
LN "unicodedata" "http://www.python.org/doc/current/lib/module-unicodedata.html"
LN "stringprep" "http://www.python.org/doc/current/lib/module-stringprep.html"
LN "pydoc" "http://www.python.org/doc/current/lib/module-pydoc.html"
LN "doctest" "http://www.python.org/doc/current/lib/module-doctest.html"
LN "unittest" "http://www.python.org/doc/current/lib/module-unittest.html"
LN "test" "http://www.python.org/doc/current/lib/module-test.html"
LN "test.test_support" "http://www.python.org/doc/current/lib/module-test.testsupport.html"
LN "math" "http://www.python.org/doc/current/lib/module-math.html"
LN "cmath" "http://www.python.org/doc/current/lib/module-cmath.html"
LN "random" "http://www.python.org/doc/current/lib/module-random.html"
LN "whrandom" "http://www.python.org/doc/current/lib/module-whrandom.html"
LN "bisect" "http://www.python.org/doc/current/lib/module-bisect.html"
LN "heapq" "http://www.python.org/doc/current/lib/module-heapq.html"
LN "array" "http://www.python.org/doc/current/lib/module-array.html"
LN "sets" "http://www.python.org/doc/current/lib/module-sets.html"
LN "itertools" "http://www.python.org/doc/current/lib/module-itertools.html"
LN "ConfigParser" "http://www.python.org/doc/current/lib/module-ConfigParser.html"
LN "fileinput" "http://www.python.org/doc/current/lib/module-fileinput.html"
LN "xreadlines" "http://www.python.org/doc/current/lib/module-xreadlines.html"
LN "calendar" "http://www.python.org/doc/current/lib/module-calendar.html"
LN "cmd" "http://www.python.org/doc/current/lib/module-cmd.html"
LN "shlex" "http://www.python.org/doc/current/lib/module-shlex.html"
LN "os" "http://www.python.org/doc/current/lib/module-os.html"
LN "os.path" "http://www.python.org/doc/current/lib/module-os.path.html"
LN "dircache" "http://www.python.org/doc/current/lib/module-dircache.html"
LN "stat" "http://www.python.org/doc/current/lib/module-stat.html"
LN "statcache" "http://www.python.org/doc/current/lib/module-statcache.html"
LN "statvfs" "http://www.python.org/doc/current/lib/module-statvfs.html"
LN "filecmp" "http://www.python.org/doc/current/lib/module-filecmp.html"
LN "popen2" "http://www.python.org/doc/current/lib/module-popen2.html"
LN "datetime" "http://www.python.org/doc/current/lib/module-datetime.html"
LN "time" "http://www.python.org/doc/current/lib/module-time.html"
LN "sched" "http://www.python.org/doc/current/lib/module-sched.html"
LN "mutex" "http://www.python.org/doc/current/lib/module-mutex.html"
LN "getpass" "http://www.python.org/doc/current/lib/module-getpass.html"
LN "curses" "http://www.python.org/doc/current/lib/module-curses.html"
LN "curses.textpad" "http://www.python.org/doc/current/lib/module-curses.textpad.html"
LN "curses.wrapper" "http://www.python.org/doc/current/lib/module-curses.wrapper.html"
LN "curses.ascii" "http://www.python.org/doc/current/lib/module-curses.ascii.html"
LN "curses.panel" "http://www.python.org/doc/current/lib/module-curses.panel.html"
LN "getopt" "http://www.python.org/doc/current/lib/module-getopt.html"
LN "optparse" "http://www.python.org/doc/current/lib/module-optparse.html"
LN "tempfile" "http://www.python.org/doc/current/lib/module-tempfile.html"
LN "errno" "http://www.python.org/doc/current/lib/module-errno.html"
LN "glob" "http://www.python.org/doc/current/lib/module-glob.html"
LN "shutil" "http://www.python.org/doc/current/lib/module-shutil.html"
LN "locale" "http://www.python.org/doc/current/lib/module-locale.html"
LN "gettext" "http://www.python.org/doc/current/lib/module-gettext.html"
LN "logging" "http://www.python.org/doc/current/lib/module-logging.html"
LN "signal" "http://www.python.org/doc/current/lib/module-signal.html"
LN "socket" "http://www.python.org/doc/current/lib/module-socket.html"
LN "select" "http://www.python.org/doc/current/lib/module-select.html"
LN "thread" "http://www.python.org/doc/current/lib/module-thread.html"
LN "threading" "http://www.python.org/doc/current/lib/module-threading.html"
LN "dummy_thread" "http://www.python.org/doc/current/lib/module-dummythread.html"
LN "dummy_threading" "http://www.python.org/doc/current/lib/module-dummythreading.html"
LN "Queue" "http://www.python.org/doc/current/lib/module-Queue.html"
LN "mmap" "http://www.python.org/doc/current/lib/module-mmap.html"
LN "anydbm" "http://www.python.org/doc/current/lib/module-anydbm.html"
LN "dbhash" "http://www.python.org/doc/current/lib/module-dbhash.html"
LN "whichdb" "http://www.python.org/doc/current/lib/module-whichdb.html"
LN "bsddb" "http://www.python.org/doc/current/lib/module-bsddb.html"
LN "dumbdbm" "http://www.python.org/doc/current/lib/module-dumbdbm.html"
LN "zlib" "http://www.python.org/doc/current/lib/module-zlib.html"
LN "gzip" "http://www.python.org/doc/current/lib/module-gzip.html"
LN "bz2" "http://www.python.org/doc/current/lib/module-bz2.html"
LN "zipfile" "http://www.python.org/doc/current/lib/module-zipfile.html"
LN "tarfile" "http://www.python.org/doc/current/lib/module-tarfile.html"
LN "readline" "http://www.python.org/doc/current/lib/module-readline.html"
LN "rlcompleter" "http://www.python.org/doc/current/lib/module-rlcompleter.html"
LN "posix" "http://www.python.org/doc/current/lib/module-posix.html"
LN "pwd" "http://www.python.org/doc/current/lib/module-pwd.html"
LN "grp" "http://www.python.org/doc/current/lib/module-grp.html"
LN "crypt" "http://www.python.org/doc/current/lib/module-crypt.html"
LN "dl" "http://www.python.org/doc/current/lib/module-dl.html"
LN "dbm" "http://www.python.org/doc/current/lib/module-dbm.html"
LN "gdbm" "http://www.python.org/doc/current/lib/module-gdbm.html"
LN "termios" "http://www.python.org/doc/current/lib/module-termios.html"
LN "TERMIOS" "http://www.python.org/doc/current/lib/module-TERMIOSuppercase.html"
LN "tty" "http://www.python.org/doc/current/lib/module-tty.html"
LN "pty" "http://www.python.org/doc/current/lib/module-pty.html"
LN "fcntl" "http://www.python.org/doc/current/lib/module-fcntl.html"
LN "pipes" "http://www.python.org/doc/current/lib/module-pipes.html"
LN "posixfile" "http://www.python.org/doc/current/lib/module-posixfile.html"
LN "resource" "http://www.python.org/doc/current/lib/module-resource.html"
LN "nis" "http://www.python.org/doc/current/lib/module-nis.html"
LN "syslog" "http://www.python.org/doc/current/lib/module-syslog.html"
LN "commands" "http://www.python.org/doc/current/lib/module-commands.html"
LN "hotshot" "http://www.python.org/doc/current/lib/module-pdb.html"
LN "timeit" "http://www.python.org/doc/current/lib/module-hotshot.stats.html"
LN "webbrowser" "http://www.python.org/doc/current/lib/module-webbrowser.html"
LN "cgi" "http://www.python.org/doc/current/lib/module-cgi.html"
LN "cgitb" "http://www.python.org/doc/current/lib/module-cgitb.html"
LN "urllib" "http://www.python.org/doc/current/lib/module-urllib.html"
LN "urllib2" "http://www.python.org/doc/current/lib/module-urllib2.html"
LN "httplib" "http://www.python.org/doc/current/lib/module-httplib.html"
LN "ftplib" "http://www.python.org/doc/current/lib/module-ftplib.html"
LN "gopherlib" "http://www.python.org/doc/current/lib/module-gopherlib.html"
LN "poplib" "http://www.python.org/doc/current/lib/module-poplib.html"
LN "imaplib" "http://www.python.org/doc/current/lib/module-imaplib.html"
LN "nntplib" "http://www.python.org/doc/current/lib/module-nntplib.html"
LN "smtplib" "http://www.python.org/doc/current/lib/module-smtplib.html"
LN "telnetlib" "http://www.python.org/doc/current/lib/module-telnetlib.html"
LN "urlparse" "http://www.python.org/doc/current/lib/module-urlparse.html"
LN "SocketServer" "http://www.python.org/doc/current/lib/module-SocketServer.html"
LN "BaseHTTPServer" "http://www.python.org/doc/current/lib/module-BaseHTTPServer.html"
LN "SimpleHTTPServer" "http://www.python.org/doc/current/lib/module-SimpleHTTPServer.html"
LN "CGIHTTPServer" "http://www.python.org/doc/current/lib/module-CGIHTTPServer.html"
LN "Cookie" "http://www.python.org/doc/current/lib/module-Cookie.html"
LN "xmlrpclib" "http://www.python.org/doc/current/lib/module-xmlrpclib.html"
LN "SimpleXMLRPCServer" "http://www.python.org/doc/current/lib/module-SimpleXMLRPCServer.html"
LN "DocXMLRPCServer" "http://www.python.org/doc/current/lib/module-DocXMLRPCServer.html"
LN "asyncore" "http://www.python.org/doc/current/lib/module-asyncore.html"
LN "asynchat" "http://www.python.org/doc/current/lib/module-asynchat.html"
LN "formatter" "http://www.python.org/doc/current/lib/module-formatter.html"
LN "email" "http://www.python.org/doc/current/lib/module-email.html"
LN "mailcap" "http://www.python.org/doc/current/lib/module-email.Message.html"
LN "mailbox" "http://www.python.org/doc/current/lib/module-mailbox.html"
LN "mhlib" "http://www.python.org/doc/current/lib/module-mhlib.html"
LN "mimetools" "http://www.python.org/doc/current/lib/module-mimetools.html"
LN "mimetypes" "http://www.python.org/doc/current/lib/module-mimetypes.html"
LN "MimeWriter" "http://www.python.org/doc/current/lib/module-MimeWriter.html"
LN "mimify" "http://www.python.org/doc/current/lib/module-mimify.html"
LN "multifile" "http://www.python.org/doc/current/lib/module-multifile.html"
LN "rfc822" "http://www.python.org/doc/current/lib/module-rfc822.html"
LN "base64" "http://www.python.org/doc/current/lib/module-base64.html"
LN "binascii" "http://www.python.org/doc/current/lib/module-binascii.html"
LN "binhex" "http://www.python.org/doc/current/lib/module-binhex.html"
LN "quopri" "http://www.python.org/doc/current/lib/module-quopri.html"
LN "uu" "http://www.python.org/doc/current/lib/module-uu.html"
LN "xdrlib" "http://www.python.org/doc/current/lib/module-xdrlib.html"
LN "netrc" "http://www.python.org/doc/current/lib/module-netrc.html"
LN "robotparser" "http://www.python.org/doc/current/lib/module-robotparser.html"
LN "csv" "http://www.python.org/doc/current/lib/module-csv.html"
LN "HTMLParser" "http://www.python.org/doc/current/lib/module-HTMLParser.html"
LN "sgmllib" "http://www.python.org/doc/current/lib/module-sgmllib.html"
LN "htmllib" "http://www.python.org/doc/current/lib/module-htmllib.html"
LN "htmlentitydefs" "http://www.python.org/doc/current/lib/module-htmlentitydefs.html"
LN "xml.parsers.expat" "http://www.python.org/doc/current/lib/module-xml.parsers.expat.html"
LN "xml.dom" "http://www.python.org/doc/current/lib/module-xml.dom.html"
LN "xml.dom.minidom" "http://www.python.org/doc/current/lib/module-xml.dom.minidom.html"
LN "xml.dom.pulldom" "http://www.python.org/doc/current/lib/module-xml.dom.pulldom.html"
LN "xml.sax" "http://www.python.org/doc/current/lib/module-xml.sax.html"
LN "xml.sax.handler" "http://www.python.org/doc/current/lib/module-xml.sax.handler.html"
LN "xml.sax.saxutils" "http://www.python.org/doc/current/lib/module-xml.sax.saxutils.html"
LN "xml.sax.xmlreader" "http://www.python.org/doc/current/lib/module-xml.sax.xmlreader.html"
LN "xmllib" "http://www.python.org/doc/current/lib/module-xmllib.html"
LN "audioop" "http://www.python.org/doc/current/lib/module-audioop.html"
LN "imageop" "http://www.python.org/doc/current/lib/module-imageop.html"
LN "aifc" "http://www.python.org/doc/current/lib/module-aifc.html"
LN "sunau" "http://www.python.org/doc/current/lib/module-sunau.html"
LN "wave" "http://www.python.org/doc/current/lib/module-wave.html"
LN "chunk" "http://www.python.org/doc/current/lib/module-chunk.html"
LN "colorsys" "http://www.python.org/doc/current/lib/module-colorsys.html"
LN "rgbimg" "http://www.python.org/doc/current/lib/module-rgbimg.html"
LN "imghdr" "http://www.python.org/doc/current/lib/module-imghdr.html"
LN "sndhdr" "http://www.python.org/doc/current/lib/module-sndhdr.html"
LN "ossaudiodev" "http://www.python.org/doc/current/lib/module-ossaudiodev.html"
LN "hmac" "http://www.python.org/doc/current/lib/module-hmac.html"
LN "md5" "http://www.python.org/doc/current/lib/module-md5.html"
LN "sha" "http://www.python.org/doc/current/lib/module-sha.html"
LN "mpz" "http://www.python.org/doc/current/lib/module-mpz.html"
LN "rotor" "http://www.python.org/doc/current/lib/module-rotor.html"
LN "Tkinter" "http://www.python.org/doc/current/lib/module-Tkinter.html"
LN "Tix" "http://www.python.org/doc/current/lib/module-Tix.html"
LN "ScrolledText" "http://www.python.org/doc/current/lib/module-ScrolledText.html"
LN "turtle" "http://www.python.org/doc/current/lib/module-turtle.html"
LN "rexec" "http://www.python.org/doc/current/lib/module-rexec.html"
LN "Bastion" "http://www.python.org/doc/current/lib/module-Bastion.html"
LN "parser" "http://www.python.org/doc/current/lib/module-parser.html"
LN "symbol" "http://www.python.org/doc/current/lib/module-symbol.html"
LN "token" "http://www.python.org/doc/current/lib/module-token.html"
LN "keyword" "http://www.python.org/doc/current/lib/module-keyword.html"
LN "tokenize" "http://www.python.org/doc/current/lib/module-tokenize.html"
LN "tabnanny" "http://www.python.org/doc/current/lib/module-tabnanny.html"
LN "pyclbr" "http://www.python.org/doc/current/lib/module-pyclbr.html"
LN "py_compile" "http://www.python.org/doc/current/lib/module-pycompile.html"
LN "compileall" "http://www.python.org/doc/current/lib/module-compileall.html"
LN "dis" "http://www.python.org/doc/current/lib/module-dis.html"
LN "distutils" "http://www.python.org/doc/current/lib/module-distutils.html"
LN "al" "http://www.python.org/doc/current/lib/module-compiler.html"
LN "AL" "http://www.python.org/doc/current/lib/module-al-constants.html"
LN "cd" "http://www.python.org/doc/current/lib/module-cd.html"
LN "fl" "http://www.python.org/doc/current/lib/module-fl.html"
LN "FL" "http://www.python.org/doc/current/lib/module-fl-constants.html"
LN "flp" "http://www.python.org/doc/current/lib/module-flp.html"
LN "fm" "http://www.python.org/doc/current/lib/module-fm.html"
LN "gl" "http://www.python.org/doc/current/lib/module-gl.html"
LN "DEVICE" "http://www.python.org/doc/current/lib/module-DEVICE.html"
LN "GL" "http://www.python.org/doc/current/lib/module-gl-constants.html"
LN "imgfile" "http://www.python.org/doc/current/lib/module-imgfile.html"
LN "jpeg" "http://www.python.org/doc/current/lib/module-jpeg.html"
LN "sunaudiodev" "http://www.python.org/doc/current/lib/module-sunaudiodev.html"
LN "SUNAUDIODEV" "http://www.python.org/doc/current/lib/module-sunaudiodev-constants.html"
LN "msvcrt" "http://www.python.org/doc/current/lib/module-msvcrt.html"
LN "_winreg" "http://www.python.org/doc/current/lib/module--winreg.html"
LN "winsound" "http://www.python.org/doc/current/lib/module-winsound.html"

# Default to the PythonInfo wiki, as a matter of convenience.

NS "PythonInfo" "http://wrap.localnames.taoriver.net/spaces/pythoninfo/"
.  "PI" .
.  "wiki" .
.  "TheWiki" .

# for caching name servers

X INVALIDATE-UPON-CHANGE-TO http://www.python.org/moin/LibraryReferenceNames?action=edit

# Bring people back here in the event that something was missing.

FINAL http://www.python.org/moin/LibraryReferencesNames?action=edit

# }}}
"""

'''A laaarge namespace description on the PythonInfo wiki.'''


## DELETE THIS SECTION IN 2006
## def return_basic_namespaces(url):
##     """Simple namespace builder, used during tests.
    
##     Why? Because I do most of my testing in the bus, without access
##     to the Internet. So I need a url-to-text builder that doesn't
##     require Internet access. Hence this function. It pretends to be
##     the Internet, returning text in response to url requests. In
##     this case, it always returns basic_text.
##     """
##     if url == "http://example.net/":
##         return neighbor_text
##     if url == "http://pythoninfo.wiki/":
##         return pythoninfo_text
##     return basic_text


class QuotationTests(unittest.TestCase):
    
    """Test quoting and unquoting.
    
    DOC
    
    testQuote  -- DOC
    testUnquote  -- DOC
    testStrange  -- DOC
    """
    
    # testQuote & testUnquote share several tests, which we store here.
    
    L = [('foo', '"foo"'),
         ('foo bar', '"foo bar"'),
         ('foo\nbar', '"foo\\nbar"'),
         ('0123456789', '"0123456789"'),
         ('"roborally"', '"\\"roborally\\""')]
    
    def testQuote(self):
        """Test generic quotes via list."""
        for (first, second) in QuotationTests.L:
            assert lncore.quote(first) == second, (first, second)
    
    def testUnquote(self):
        """Test generic unquotes via list."""
        for (first, second) in QuotationTests.L:
            assert lncore.unquote(second) == first, (first, second)
    
    def testStrange(self):
        """Test cases that are likely to fail in first lncore.
        
        These are tests that should pass, but are harder to code for.
        They are rare, but we eventually want to code to solve them.
        """
        pass


class LineTests(unittest.TestCase):
    
    """Test line recognition.
    
    DOC
    
    testRecordInterpretation  -- test record details
    testLineInterpretation  -- test line types
    """
    
    records = [('LN "foo" "http://example.com/"',
                lncore.LN, "foo", "http://example.com/"),
               ('NS "foo" "http://example.com/"',
                lncore.NS, "foo", "http://example.com/"),
               ('X "foo" "http://example.com/"',
                lncore.X, "foo", "http://example.com/"),
               ('PATTERN "foo" "http://example.com/"',
                lncore.PATTERN, "foo", "http://example.com/"),]
    
    lines = [('LN "foo" "http://example.com/"', lncore.Line.RCD),
             ('# This is a comment."', lncore.Line.CMT),
             ('', lncore.Line.BLK),
             ('An error.', lncore.Line.ERR),]
    
    def testRecordInterpretation(self):
        """Test details of record line interpretation."""
        for (line, record_type, key, value) in LineTests.records:
            line = lncore.Line(line)
            assert line.record_type == record_type
            assert line.key == key
            assert line.value == value
    
    def testLineInterpretation(self):
        """Test that line types are proprely recognized."""
        for (line, line_type) in LineTests.lines:
            line = lncore.Line(line)
            assert line.line_type == line_type


class TokenizingTest(unittest.TestCase):
    
    """DOC
    
    DOC
    
    DOC
    """
    
    results = [(lncore.Line.BLK,
                None, None, None),
               (lncore.Line.RCD,
                lncore.X, "VERSION", "1.2"),
               (lncore.Line.RCD,
                lncore.LN, "foo", "http://example.com/"),
               (lncore.Line.RCD,
                lncore.LN, "bar", "http://example.com/"),
               (lncore.Line.RCD,
                lncore.X, "FINAL", "http://example.com/$NAME"),
               (lncore.Line.RCD,
                lncore.NS, "neighbor", "http://example.net/"),
               (lncore.Line.RCD,
                lncore.PATTERN, "pat",
                "http://example.com/$ARG1/$ARG2/"),
               (lncore.Line.BLK,
                None, None, None),]
    
    def testLines(self):
        """DOC"""
        lines = lncore.text_to_lines(basic_text)
        specs = TokenizingTest.results
        for (line, spec) in zip(lines, specs):
            (line_type, record_type, key, value) = spec
            assert line.line_type == line_type, line.line_type
            assert line.record_type == record_type
            assert line.key == key
            assert line.value == value, spec


class NamespaceTest(unittest.TestCase):
    
    """Test namespace functionality.
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        """Create a namespace to test from the basic text."""
        lines = lncore.text_to_lines(basic_text)
        self.namespace = lncore.lines_to_namespace(lines)
    
    def testConversionFromText(self):
        """Check values in the namespace."""
        assert self.namespace[lncore.LN]["foo"] == "http://example.com/"
        assert self.namespace[lncore.LN]["bar"] == "http://example.com/"
        assert self.namespace[lncore.X]["VERSION"] == ["1.2"]
    
    def testFinal(self):
        """Check that X FINAL replacement works properly."""
        assert self.namespace.final("foo") == (0, "http://example.com/foo")
    
    def testBulletinBoard(self):
        """Check that the bulletin board keeps entries separate."""
        self.namespace.get_bboard("FOO")["foo"] = "AAA"
        self.namespace.get_bboard("BAR")["foo"] = "ZZZ"
        assert self.namespace.get_bboard("FOO")["foo"] == "AAA"


class UrlTemplateTest(unittest.TestCase):
    
    """Test URL templates.
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        """Create simple URL templates."""
        self.pattern = lncore.UrlTemplate("http://example.com/$NAME")
        args_text = "http://example.com/$ARG1/$ARG2/$ARG3"
        self.args_pattern = lncore.UrlTemplate(args_text)
    
    def testNameReplacement(self):
        """DOC"""
        assert self.pattern.replace("foo") == (0,
                                               "http://example.com/foo")
    
    def testArgsReplacement(self):
        """DOC"""
        val = self.args_pattern.replace(["foo", "bar", "baz"])
        assert val == (0, "http://example.com/foo/bar/baz")

    def testNeedMoreArgs(self):
        """DOC"""
        val = self.args_pattern.replace(["foo", "bar"])
        assert val[0] == -202


class TestThatUsesTestStore(unittest.TestCase):

    """Super-class for tests that use the TestStore.

    DOC - children need call setUp if override.

    DOC
    """
    
    def setUp(self):
        """Create simple Store."""
        self.store = lncore.TestStore()
        self.store.bind("http://example.com/", basic_text)
        self.store.bind("http://example.net/", neighbor_text)
        self.store.bind("http://pythoninfo.wiki/", pythoninfo_text)


class StoreTest(TestThatUsesTestStore):
    
    """Test the test namespace description Store.

    It feels a bit silly to test a test store, and perhaps it is. But
    there are other tests that are going to rely on the TestStore, and I
    want to make sure that it's actually working like I think it does.

    DOC
    
    DOC
    """
    
    def testCaching(self):
        """Make sure that the store is caching namespaces."""
        ns1 = self.store("http://example.com/")
        ns1.get_bboard("test")["flag"] = True
        ns2 = self.store("http://example.com/")
        assert ns1.get_bboard("test")["flag"] == True

    def testCacheList(self):
        """Make sure that get_cache_list works."""
        must_have = [("", "http://example.com/", 1000),
                     ("", "http://example.net/", 1000),
                     ("", "http://pythoninfo.wiki/", 1000),]
        result = self.store.get_cache_list()
        for (a,b,c) in must_have:
            assert (a,b,c) in result
        assert len(result) == len(must_have)


class TraditionalStyleTest(TestThatUsesTestStore):
    
    """Test Traditional Style resolution.
    
    DOC
    
    DOC: JUST THOUGHTS; REWORK OR DELETE THEM LATER:
    We want to make sure that:
    * It resolves a correctly spelled name.
    * It resolves a closely spelled name.
    * It resolves a name found in a neighboring namespace.
    * It resolves a closely spelled name in a neighboring namespace.
    * That it can namespace hop.
    * That PATTERNs are resolved.
    * That X "FINAL" works.
    
    DOC
    """
    
    L = [("LN", "foo", "http://example.com/"),
         ("LN", "bar", "http://example.com/"),
         ("LN", "foos", "http://example.com/"),
         ("LN", "baz boz", "http://example.net/bazboz/"),
         ("LN", "bazboz", "http://example.net/bazboz/"),
         ("LN", ["neighbor", "baz boz"], "http://example.net/bazboz/"),
         ("LN", ["pat", "foo", "bar"], "http://example.com/foo/bar/"),
         ("LN", "beer", "http://example.com/beer"),
         ("NS", "neighbor", "http://example.net/"),
         ("PATTERN", "pat", "http://example.com/$ARG1/$ARG2/"),
         ("X", "FINAL", ["http://example.com/$NAME"]),
         ("X", "VERSION", ["1.2"]),]

    M = [("LN", ["NumericTypes"],
          "http://www.python.org/doc/current/lib/typesnumeric.html"),]
    
    def setUp(self):
        """DOC"""
        TestThatUsesTestStore.setUp(self)
        self.style = lncore.Traditional(self.store)

    def performTests(self, namespace_url, test_list):
        """Perform several lookups in Traditional Style."""
        for (record_type, lookup, url) in test_list:
            result = self.style.find(namespace_url,
                                     lookup, record_type)
            assert result == (0, url), result
    
    def testBasicLookups(self):
        """Try out basic lookups on the Traditional Style."""
        self.performTests("http://example.com/", TraditionalStyleTest.L)

    def testLongLookups(self):
        """Try out lookups on the larger PythonInfo namespace."""
        self.performTests("http://pythoninfo.wiki/",
                          TraditionalStyleTest.M)


class TestKeyHashOrderedDictionary(unittest.TestCase):
    
    """DOC
    
    DOC
    
    DOC
    """
    
    def setUp(self):
        """DOC"""
        self.D = lncore.KeyHashOrderedDictionary()
        self.D["foo bar"] = "baz"
        self.D["baz boz"] = "foo bar"
    
    def testRetrieval(self):
        """DOC"""
        assert self.D["foobar"] == "baz"
        assert self.D["baz   boz"] == "foo bar"
    
    def testDelete(self):
        """DOC"""
        del self.D["foo bars"]
        assert self.D.get("foo bar") == None
    
    def testLoad(self):
        """Testing loading data from another ordered dictionary."""
        ordered = lncore.OrderedDictionary()
        ordered["foo bar"] = "baz"
        ordered["baz boz"] = "foo bar"
        keyhash = lncore.KeyHashOrderedDictionary()
        keyhash.load_from(ordered)
        assert keyhash.order() == ["foobar", "bazboz"]
        assert keyhash["foobar"] == "baz"
        assert keyhash["baz   boz"] == "foo bar"


class TestDefaultStyle(unittest.TestCase):

    """Test that "default" returns the first listed style.

    DOC

    testDefault   -- DOC
    """

    def testDefault(self):
        assert lncore.find_style("default") == lncore.styles[0]


class TestBasicRelativeURLHandlingBehavior(unittest.TestCase):

    """DOC

    DOC

    DOC
    """

    def testBasic(self):
        """Test that basic relative URL handling behavior works."""
        ns_url = "http://www.example.com/foo/namespace.txt"
        relative_url = "bar.txt"
        final_url = "http://www.example.com/foo/bar.txt"
        x = lncore.basic_relative_url_handling_behavior(relative_url,
                                                        ns_url)
        assert x == final_url

    def testPassingAnAbsolute(self):
        """Test that absolute URLs are not handled specially."""
        ns_url = "http://www.example.com/foo/namespace.txt"
        absolute_url = "http://www.example.com/bar.txt"
        x = lncore.basic_relative_url_handling_behavior(absolute_url,
                                                        ns_url)
        assert x == absolute_url


if __name__ == "__main__":
    unittest.main() # run all tests

