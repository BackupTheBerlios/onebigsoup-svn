


import xmlrpclib



class PlogServer:
    def __init__( self, url ):
        self.serverproxy = xmlrpclib.ServerProxy( url )
    def user( self, name ):
        return PlogUser( self.serverproxy, name )
    def users( self ):
        return self.serverproxy.all_users()

class PlogUser:
    def __init__( self, server, username ):
        self.server = server
        self.username = username

    def __setitem__( self, key, value ):
        self.server.store( self.username, key, value )
    def __getitem__( self, key ):
        return self.server.retrieve( self.username, key )
    
    def log( self, logtype, logdata ):
        self.server.log( self.username,
                         logtype,
                         logdata )
    def log_pageview( self, url ):
        self.log( "pageview",
                  { "URL": url } )
    def log_wikipost( self,
                      wiki_name, wiki_url,
                      page_name, page_url,
                      comment ):
        self.log( "wikipost",
                  { "InterWikiName": wiki_name,
                    "WikiURL": wiki_url,
                    "PageName": page_name,
                    "PageURL": page_url,
                    "Comment": comment } )
        
    def get_logs( self, logtype, maxnum=10, maxage=(60*60) ):
        """Defaults to list 10 items, maximum age 1 hour ago."""
        return self.server.get_logs( self.username,
                                     logtype, maxnum, maxage )


