import time
import feedparser
import xmlrpclib
import pickle
import socket

class DingDing:
   def __init__(s, URL, pw):
     s.URL=URL
     s.pw=pw
   def notify(s, load):
      notified = 0
      while not notified:
         try:
            xmlrpclib.ServerProxy(s.URL).notify(load, s.pw)
            notified=1
            print time.asctime(), "notified", load
         except socket.timeout:
            print time.asctime(), "wasn't able to notify... sleeping 5 seconds."
            time.sleep(5) # wait five seconds...

class Scanner:
   def __init__(s, rss_URL, period, dingding, state_filename):
     s.rss_URL = rss_URL
     s.period = period
     s.dingding = dingding
     s.state_filename = state_filename
     
     try:
       file = open(state_filename, "r")
       s.lastseen=pickle.load(file)
     except IOError:
       s.lastseen = None
        
   def loop(s):
     feed=feedparser.parse(s.rss_URL)
     ents=feed["entries"]
     matches=[x for x in range(len(ents)) if ents[x]["link"]==s.lastseen]
     if len(matches)>0:
       ents=ents[:matches[0]]
     for entry in ents:
       load={"Action":"wikipost2",
             "Comment":entry.get("description", "(no comment)"),
             "InterWikiName":feed["feed"]["wiki_interwiki"],
             "WikiUrl":feed["feed"]["link"],
             "PageName":entry["title"],
             "PageUrl":entry["link"],
             "TimeEventHappened":entry["date"][:19],
            }
       
       load["TransparencyText"] = """Posted to %(InterWikiName)s:%(PageName)s - %(Comment)s""" % load
       load["TransparencyXhtml"] = """Posted to <a href="%(WikiUrl)s">%(InterWikiName)s</a>:<a href="%(PageUrl)s">%(PageName)s</a> - %(Comment)s""" % load
       load["TransparencyXhtmlColumnHeaders"] = [ "Wiki", "Page", "Comment" ]
       load["TransparencyXhtmlRow"] = [ """<a href="%(WikiUrl)s">%(InterWikiName)s</a>""" % load, """<a href="%(PageUrl)s">%(PageName)s</a>""" % load, "%(Comment)s" % load ]

       if entry.get( "dc_contributor" ) == "LionKimbro":
          load["UserName"] = entry["dc_contributor"]
       
       s.dingding.notify(load)

     s.lastseen = feed["entries"][0]["link"]
     file=open(s.state_filename, "w")
     pickle.dump(s.lastseen, file)

     time.sleep(s.period)

if __name__ == "__main__":
  dingding=DingDing("http://services.taoriver.net:9011/", "password")
  scanner=Scanner("http://www.emacswiki.org/cgi-bin/community?action=rss", 10*60, dingding, "cw.p")
  while 1:
    print time.asctime(), "Scanning, Dave..."
    scanner.loop()
    
