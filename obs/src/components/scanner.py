import feedparser
import xmlrpclib
import time

eventserver_url = "http://services.taoriver.net:9012"
eventserver_password = "password"

list_of_scanners= [
     {"link":"http://www.speakeasy.org/~lion/lionsden.rss", 
      "timer-in-seconds":5,
      "load":{ "Action": "blog post", "Author": "Lion" }
      },
     {"link":"http://wiki.subtlehints.net/moin/RecentChanges?action=rss_rc",
      "timer-in-seconds":60*60,
      "load":{ "Action": "wiki edit" }
      }]

                 
class Scanner:
  def __init__(s, url, password, link, timer_in_seconds, load):
    s.url = url
    s.password = password
    s.link = link
    s.timer_in_seconds = timer_in_seconds
    s.load = load
    s.last_checked = time.time()
    s.last_feed = feedparser.parse(s.link)
    
  def ready_yet(s):
    return time.time() - s.last_checked >= s.timer_in_seconds
    
  def update(s):
    if not s.ready_yet():
      return
    feed = feedparser.parse(s.link)
    for item in feed["items"]:
      if not s.have_seen_before(item):
        s.post(item)
    s.last_feed = feed
    
  def have_seen_before(s, search_for):
    for item in s.last_feed["items"]:
      if search_for == item:
        return True
    return False
    
  def post(s, item):
    server = xmlrpclib.ServerProxy(s.url)
    load = s.load.copy()
    load["data-from-feed"] = item
    print "Notifying server of %s" % load
    server.notify(load, s.password)
    

if __name__ == "__main__":
  scanners = []
  for spec in list_of_scanners:
    scanners.append( Scanner(eventserver_url,
                       eventserver_password,
                       spec["link"],
                       spec["timer-in-seconds"],
                       spec["load"] ))
                       
  while True:
    print "Scanning..."
    for scanner in scanners:
      scanner.update()
    time.sleep(10)
