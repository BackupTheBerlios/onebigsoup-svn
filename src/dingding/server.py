"""
DingDing XML-RPC Event Server

In some cases, this may actually be-
  Wiki:TheSimplestThingThatCouldPossiblyWork.

----

 + (./) get_logs( pattern )
 + "IN-LAST-N-SECONDS"
 + (./) standard received time stamp format (ISO8601 DateTime)
     - *./) screw standards. We'll just use RESERVED information.
 + update conventions doc
"""

import time
import httplib,xmlrpclib
import futures
import cPickle as pickle
from DocXMLRPCServer import DocXMLRPCServer



HOST_NAME    = "services.taoriver.net"
PORT_NUMBER = 9011
PASSWORD    = "password"

SUBSCRIPTIONS_PICKLE = "registry.p"
LOGS_PICKLE = "log.p"
LOGS_PUBLIC = True
MAX_LOGS_KEPT = 1000
MAX_LOGS_RETURNED = 50



class Server:
    """
    Functions you can call:

    * notify( load, Spw )                     - report an event
    * subscribe( pattern, client_info, Cpw )   - ask for notice of events
    * unsubscribe( pattern, client_info, Cpw ) - ask for no more notices

    load:    A dictionary of NLSD data summarizing the event.
             (NLSD: Numbers, Lists, Strings, Dictionaries)
    Spw:     Server "Post" password - password required
             to post events to the event server.
             Minimal protection against attack.
    Cpw:     Client "Post" password - password required
             to post events to the clienct server.
             Also used to guard against unautherized
             unsubscription, thus required in
             calls to "unsubscribe".
             Minimal protection against attack.
    client_info: A dictionary of information about the client.
                 At a minimum, post "CLIENT-URL".
             "CLIENT-XMLRPC": Client XML-RPC URL.
             "PUBLIC-VIEWING": 0 if request hidden,
                               1 if public can know subscription
    pattern: Event-matching pattern. Lists of lists of strings.
             Possibilities:
             ["ALL"]
             ["VAL", var-name, str-val]
             ["INCL", var-name, str-val]
             ["NOT", pattern]
             ["AND", pattern, ... ]
             ["OR", pattern, ... ]
             ["IN-LAST-N-SECONDS", num-seconds ]
             Examples:
             * ["ALL"]
             * ["VAL", "Author", "LionKimbro"]
             * ["AND",
                 ["VAL", "Author", "LionKimbro"],
                 ["INCL", "Comment", "(blog)"]]
    
    A password is required to report events,
    but not to subscribe to them.

    ! ! ! ! !
    
    The password is plaintext. Thus, this protocol
    is EXTREMELY SUSCEPTABLE TO SNIFFING.

    The password for this server should be different
    than any other password you use. It is COMPLETELY
    TRANSPARENT to attack.

    ! ! ! ! !
    """
    def __init__( s, host_name, port_number, password ):
        s.host_name = host_name
        s.port_number = port_number
        s.password = password

        s.registry = []     # (ptrn, client_info, Cpw),...
        s._load()

    def _load(s):
        try:
            s.registry = pickle.load( open( SUBSCRIPTIONS_PICKLE, "r" ) )
            print time.asctime(), "-- Loaded Registry: %s" % SUBSCRIPTIONS_PICKLE
        except IOError:
            s.registry = []
            print time.asctime(),
            print "-- Clear Registry (%s nonexistant)" % SUBSCRIPTIONS_PICKLE

    def _save(s):
        pickle.dump( s.registry, open( SUBSCRIPTIONS_PICKLE, "w" ) )
        
    def _custom_reduce(s, foo, list_, early_exit, load):
        if type(list_[0]) == type([]):
            a = s._match( load, list_[0] )
        else:
            a = list_[0]
        b = s._match( load, list_[1] )
        r = foo(a, b)
        if len(list_) == 2:
            return r
        if r == early_exit:
            return r
        return _custom_reduce(foo, [r]+list_[2:], early_exit, load)

    def _match(s, load, pattern):
        op = pattern[0].upper()
        if op == "ALL":
            return True
        elif op == "NOT":
            return not s._match(load, pattern[1])
        elif op == "AND":
            return _custom_reduce(lambda x, y: x and y,
                                 pattern[1:], False, load)
        elif op == "OR":
            return _custom_reduce(lambda x, y: x or y,
                                 pattern[1:], True, load)
        elif op == "VAL":
            var_name = pattern[1]
            test_val = pattern[2]
            if not load.has_key( var_name ):
                return False
            return load[var_name] == test_val
        elif op == "INCL":
            var_name = pattern[1]
            test_val = pattern[2]
            if not load.has_key( var_name ):
                return False
            return load[var_name].find(test_val) != -1
        elif op == "IN-LAST-N-SECONDS":
            seconds_ago = pattern[1]
            time_ago = time.time()-seconds_ago
            if not load.has_key( "RESERVED-RECEIVED-TIME" ):
                return False
            return load["RESERVED-RECEIVED-TIME"] > time_ago
        raise "Bad op: " + str(op)

    def _stripped_copy( s, load ):
        """
        Strip out "RESERVED" information before resending.
        """
        copy = load.copy()
        for k in copy.keys():
            if k.startswith( "RESERVED" ):
                del copy[k]
        return copy
    
    def _ding(s, client_info, Cpw, load):
        xmlrpc_url = client_info.get( "CLIENT-XMLRPC", None )
        if xmlrpc_url:
            try:
                server=xmlrpclib.ServerProxy( xmlrpc_url )
                print time.asctime(),"-- notify %s" % xmlrpc_url
                server.notify( s._stripped_copy(load), Cpw )
                return True # success
            except httplib.socket.error:
                pass
            except xmlrpclib.Fault, f:
                pass
        print time.asctime(), "-- notice failed"
        return False # failure

    def _stampload(s,load):
        """
        Timestamp a load, with whatever value we like.
        (Reserved for server use.)
        """
        load["RESERVED-RECEIVED-TIME"] = time.time()
    def _log(s, load):
        try:
            log = pickle.load( open( LOGS_PICKLE,"r" ) )
        except IOError:
            log = []
        log.append(load)
        if len( log ) > MAX_LOGS_KEPT:
            log = log[-MAX_LOGS_KEPT:]
        pickle.dump( log, open( LOGS_PICKLE,"w" ) )

    def notify(s, load, Spw ):
        """
        Notify the event server that an event has occurred.

        load:       data (dictionary)
        Spw:        notify password (string)

        WARNING: Spw is communicated in PLAIN-TEXT!
        """
        if Spw != s.password:
            return 0

        # time-stamp the received message
        s._stampload( load )
        
        # build list of target servers to notify
        to_notify = []
        for (ptrn, rcpnt, Cpw) in s.registry:
            if s._match(load, ptrn):
                to_notify.append( (ptrn,rcpnt,Cpw) )

        # notify them en masse
        in_progress = [futures.Future(s._ding,rcpnt,Cpw,load)
                       for (ptrn,rcpnt,Cpw) in to_notify]
        results = [f() for f in in_progress]

        # remove those that no longer exist
        for (target,result) in zip(to_notify,results):
            if result == False:
                print time.asctime(), "-- removing %s" % str(target)
                s.registry.remove(target)

        # append to logs
        s._log( load )
        
        return 1

    def subscribe(s, pattern, client_info, Cpw ):
        """
        Subscribe to an event channel.

        pattern:      Event-matching pattern. Lists of lists of strings.
        client_info:  Info about client (dictionary)
        Cpw:          Client notification password
        """
        if type( client_info ) == type( "" ):
            raise "Client_info must be dictionary."
        if not client_info.has_key( "CLIENT-XMLRPC" ):
            raise "This DingDing event server can only handle XML-RPC. Define CLIENT-XMLRPC in client_info."
        s.registry.append((pattern, client_info, Cpw))
        s._save()
        return 1

    def unsubscribe(s, pattern, client_info, Cpw ):
        """
        Un-subscribe to an event channel.

        pattern:      Event-matching pattern. Lists of lists of strings.
        client_info:  Info about client (dictionary)
        Cpw:          Client notification password
        """
        indexes = range( len(s.registry) )
        indexes.reverse()
        found_one = False

        for i in indexes:
            (p,r,c) = s.registry[i]
            if Cpw==c and r==client_info and p==pattern:
                del s.registry[i]
                found_one = True

        if found_one == True:
            s._save()

        return found_one

    def get_logs( s, ptrn ):
        """
        The server is not obligated to keep logs
        for any set period of time.

        The server is not obligated to return all
        the logs that match.

        Returns newest to oldest.
        """
        to_return = []

        try:
            log = pickle.load( open( LOGS_PICKLE, "r" ) )
        except IOError:
            log = []
        
        for load in log:
            if s._match( load, ptrn ):
                to_return.append( s._stripped_copy(load) )

        to_return.reverse() # newest first
        if len( to_return ) > MAX_LOGS_RETURNED:
            to_return = to_return[:MAX_LOGS_RETURNED]
        return to_return

    def run( s ):
        server = DocXMLRPCServer( (s.host_name, s.port_number),
                                  logRequests=0 )
        server.register_function( s.notify )
        server.register_function( s.subscribe )
        server.register_function( s.unsubscribe )
        server.register_function( s.get_logs )
        print time.asctime(), "Event Server Starts - %s:%s" % (s.host_name,
                                                               s.port_number)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        print time.asctime(), "Event Server Stops - %s:%s" % (s.host_name,
                                                              s.port_number)

if __name__ == "__main__":
    server = Server( HOST_NAME, PORT_NUMBER, PASSWORD )
    server.run()
