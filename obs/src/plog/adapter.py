#!/usr/bin/env python

import time
import socket
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer


hostname = "services.taoriver.net"
port_number = 9040
adapter_password="sdjhbvouetyuovygh"
eventserver_xmlrpc_url="http://services.taoriver.net:9012/"
eventserver_password="password"
plog_xmlrpc_url="http://plog.taoriver.net:8000/"

# Adapter from DingDingv3 to Plogv1
# honors PleaseDontLogByUser bit


class Server:
    def __init__(s):
        s.plog_server=xmlrpclib.ServerProxy(plog_xmlrpc_url)

        event_server=xmlrpclib.ServerProxy(eventserver_xmlrpc_url)
        event_server.subscribe(["VAL", "Action", "edit"],
                    {"CLIENT-XMLRPC":"http://"+hostname+":"+str(port_number)+"/"},
                    adapter_password)
        
    def run( s, port_num ):
        server = SimpleXMLRPCServer((hostname, port_num), logRequests=0)
        server.register_function( s.notify )
        print time.asctime(), "Personal Log Adapter Starts - %s:%s" % (hostname,
                                                                      port_number)
        server.serve_forever()
        print time.asctime(), "Personal Log Adapter Stops - %s:%s" % (hostname,
                                                                     port_number)
    def notify(s, load, Cpw):
        if adapter_password != Cpw:
            return 0
        if not load.has_key("PleaseDontLogByUser"):
            return "Will not process without PleaseDontLogByUser = 0"
        if load["PleaseDontLogByUser"]:
            return "User requested no logging"
        if load["Action"] != "edit":
            return "Not a Wiki post"

        try:
            d={"InterWikiName":load["InterWikiName"],
               "WikiURL":load["WikiUrl"],
               "PageName":load["PageName"],
               "PageURL":load["PageUrl"],
               "Comment":load["Comment"],
               }

            s.plog_server.log(load["UserName"], "wikipost", d)
        except KeyError:
            return "Doesn't have needed keys. One of InterWikiName, WikiUrl, PageName, PageUrl, Comment, or UserName."

        return 1
        

if __name__ == "__main__":
    server = Server()
    server.run( port_number )


 
