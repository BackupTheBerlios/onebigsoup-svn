"""
Simple server that exists for the purpose of
testing DingDing. (v5 in particular)
"""

import time
import socket
from DocXMLRPCServer import DocXMLRPCServer

class DummyServer:
    def notify( s, msg, conn ):
        if conn[ "Password" ] != "password":
            return 0
        print msg
        return 1

if __name__ == '__main__':
    server = DocXMLRPCServer(("services.taoriver.net", 8001), logRequests=0)
    server.register_introspection_functions()
    server.register_multicall_functions()
    server.register_instance(DummyServer())

    print time.asctime(), 'Application Starting.'
    server.serve_forever()
    print time.asctime(), 'Application Finishing.'
