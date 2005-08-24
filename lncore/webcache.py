#!/usr/bin/python
"""Retrieve and cache web pages.

webcache retrieves and caches web pages. If the webpage has been
retrieved before, the cached version is used.

The module is primitive; it DOES NOT respect HTTP cache headers. Cached
pages are stored in a BSD database.

WebCache --  cache for web pages
"""

import time
import urllib
import optparse
import bsddb


class WebCache:
    
    """BSD DB cache for web pages.

    __contains__ --  URL cached, not expired?
    get_page --  retrieve a page from cache or web
    dump_page --  dump a cache entry
    time_to_live --  seconds until a page times out
    clean --  vet expired cache entries
    """
    
    def __init__(self,
                 page_db_filename="pages.db",
                 time_db_filename="times.db",
                 cache_ttl=7*24*60*60):
        """Initialize web cache.
        
        Berkeley databases are created if they don't already exist. The
        page database stores the contents of web pages. The time
        database stores the times that the pages were loaded.
        
        Times are stored in seconds since the epoch.
        
        page_db_filename --  filename of page database
        time_db_filename --  filename of load timestamp database
        cache_ttl --  cache time to live in seconds
        """
        self._page_db = bsddb.hashopen(page_db_filename)
        self._time_db = bsddb.hashopen(time_db_filename)
        self.cache_ttl = cache_ttl

    def __iter__(self):
        """DOC"""
        self.clean()
        return iter(self._time_db)

    def __contains__(self, url):
        """Return True if page is cached and hasn't expired."""
        return self.time_to_live(url) > 0
    
    def get_page(self, url):
        """Retrieve a page from the web or the cache.
        
        get_page returns the page contents retrieved by urllib.urlopen.
        
        url --  URL of web page to retrieve
        """
        
        now = time.time()
        if url in self._time_db:
            last_read = float(self._time_db[url])
            if now < last_read + self.cache_ttl:
                return self._page_db[url]
        
        contents = urllib.urlopen(url).read()
        
        self._page_db[url] = contents
        self._time_db[url] = str(now)
        self._page_db.sync()
        self._time_db.sync()
        
        return contents
    
    def time_to_live(self, url):
        """Return seconds left before cache entry expires."""
        now = time.time()
        if url in self._time_db:
            last_read = float(self._time_db[url])
            return last_read + self.cache_ttl - now
        return 0
    
    def dump_page(self, url):
        """Force a cache entry to expire."""

        del self._time_db[url]
        del self._page_db[url]
        self._time_db.sync()
        self._page_db.sync()
    
    def clean(self):
        """Vet cache of expired entries.
        
        Note that the BSD database file may not actually get smaller.
        (Rather, older data will be overwritten by new data.)
        """
        now = time.time()
        for (url, last_read) in self._time_db.items():
            last_read = float(last_read)
            if now >= last_read + self.cache_ttl:
                del self._time_db[url]
                del self._page_db[url]
        self._time_db.sync()
        self._page_db.sync()


if __name__ == "__main__":
    parser = optparse.OptionParser("usage: %prog [options]\n"
                                   "cleans the cache if no URL is"
                                   " supplied")
    parser.add_option("-p", "--pages", dest="page_db_filename",
                      default="pages.db", type="string",
                      help="pages BSD database filename")
    parser.add_option("-t", "--times", dest="time_db_filename",
                      default="times.db", type="string",
                      help="timestamps BSD database filename")
    parser.add_option("-T", "--ttl", dest="ttl", default=60*60,
                      type="int", help="time to live (in seconds)")
    parser.add_option("-u", "--url", dest="url", type="string",
                      help="url of page to retrieve and display")

    (options, args) = parser.parse_args()
    if len(args) > 0:
        parser.error("incorrect number of arguments")

    cache = WebCache(options.page_db_filename, options.time_db_filename,
                     options.ttl)
    if options.url is None:
        cache.clean()
    else:
        print cache.get_page(options.url)

