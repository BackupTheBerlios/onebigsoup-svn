"""
python2.3 server3.py password -Hservices.taoriver.net -p9009 -t"test dingdingv5 server" -d
"""

import cPickle as pickle
import BaseHTTPServer
import cgi
import xmlrpclib
import select
from xml.parsers.expat import ExpatError


class Subscription:
    """
    Subscription - augment a subscription dictionary
    """
    def __init__(s, d, dingding): # subscription dictionary
        """
        subscription dictionary:
         * MatchPattern (*REQUIRED* - pattern of data matching out)
         * XmlRpcRecvUrl (REQUIRED) - XML-RPC URL for receiving Notify messages
         * RecvPassword (OPTIONAL - used when posting a NOTIFY, also a legitimizing recipient password)
         
         * SubscriptionPasswords (OPTIONAL - group passwords that the subscription accepts messages for)
         * WhoCanSeeThis (OPTIONAL- "PUBLIC", "ADMIN-ONLY", or [list,of,group-passwords])

         * Title (OPTIONAL) - human-readable string, naming the subscription
         * Url (OPTIONAL) - a URL associated with the subscription
         * Comment (OPTIONAL) - human-readable comment, describing the subscription
        """
        s.dingding = dingding

        s.subscription_dictionary = d
        
        s.match_pattern = d[ "MatchPattern" ]
        s.xmlrpc_recv_url = d[ "XmlRpcRecvUrl" ]
        s.recv_password = d.get( "RecvPassword", None )
        
        s.subscription_passwords = d.get( "SubscriptionPasswords", [] )
        s.who_can_see_this = d.get( "WhoCanSeeThis", s.dingding.options.get_defaultcomponentvisibility() )
        
        s.title = d.get( "Title", "(untitled)" )
        s.url = d.get( "Url", None )
        s.comment = d.get( "Comment", None )

    def get_permit(s):
        """
        Emit a Permit representing what this subscription is allowed to see.

        Impossible to have an ADMIN-level subscription.
        """
        if s.subscription_passwords == []:
            return PUBLIC_PERMIT
        else:
            return Permit( s.subscription_passwords )


CONST_PERMIT_PUBLIC = "PUBLIC"
CONST_PERMIT_ADMIN = "ADMIN"

class Permit:
    """
    Permit describing viewing permissions.
    Used when talking with the DingDingCensor.

    Can be: PUBLIC, ADMIN, or list GROUPS.
    PUBLIC -- this is a permit to view what is visible to general public
    GROUPS -- this is a permit representing ability to view information
              visible to particular groups, who are listed
    ADMIN -- this is a permit to see ANYTHING
    """
    def __init__( s, permissions="PUBLIC" ):
        """
        Pass in either:
         * the string "PUBLIC"
         * the string "ADMIN"
         * a list of group passwords
        """
        if type( permissions ) == type( [] ):
            s.permission = "GROUP"
            s.groups = permissions
        elif type( permissions ) == type( "string" ):
            if permissions in [ CONST_PERMIT_PUBLIC,
                                CONST_PERMIT_ADMIN ]:
                s.permission = permissions
                s.groups = None
            else:
                raise "Do not understand permissions string type: %s" % permissions
        else:
            raise "Do not understand permissions from type of: %s" % str(permissions)
    def groups(s):
        return s.groups or []
    def is_public(s):
        return s.permission == CONST_PERMIT_PUBLIC
    def is_admin(s):
        return s.permission == CONST_PERMIT_ADMIN
    def is_groups(s):
        return s.permission == "GROUP"

PUBLIC_PERMIT = Permit( CONST_PERMIT_PUBLIC ) # shortcut
ADMIN_PERMIT = Permit( CONST_PERMIT_ADMIN ) # shortcut

class Connection:
    """
    Connection - augment a connection dictionary
    """
    def __init__( s, d, dingding ): # connection dictionary
        """
        connection dictionary:
        * Password (OPTIONAL - if not specified though, relying on target having no password requirements)
        * WhoCanSeeThis (OPTIONAL - "PUBLIC", "ADMIN-ONLY", or ["list", "of", "subscription", "passwords"])
            PUBLIC -- everyone can receive notice of what you just did/said
            ADMIN-ONLY -- only those with sys-admin priviledges to the DingDing server can see it.
            (list) -- list of subscription passwords that are authorized to receive the message
        * Destroy (OPTIONAL - if set to one, request that no incidental logs are kept of the event.)

        If WhoCanSeeThis not specified, server defaults are used. ASSUME PUBLIC, and LOGGED.
        Make it ADMIN-ONLY if you want it private to the DingDing server (and the admin), and SET DESTROY
          TO 1 if you want the admin-logs to automatically delete any incidental logs involved.
        """
        s.dingding = dingding
        s.password = d.get( "Password", None )
        s.who_can_see_this = d.get( "WhoCanSeeThis", s.dingding.options.get_defaultmessagevisibility() )
        s.destroy = d.get( "Destroy", 0 )
    def is_password(s, pword):
        return s.password == pword

class DingDing:
    """
    This is the DingDing core. It loads all DingDing instances,
    helps them keep track of each other, and serves as an event
    posting board between them. In "Design Patterns" talk, this
    is a *mediator.*
    """
    def __init__( s ):
        """
        Initialize all modules connected to the core.
        """
        s.options = DingDingOptions(s) # load command line options
        s.server = DingDingHttpServer(s) # create the HTTP server
        s.uli = DingDingUli(s) # ULI response
        s.subscriptions = DingDingSubscriptions(s)
        s.security = DingDingSecurity(s)
        s.work_orders = DingDingWorkOrders(s)
        s.notice_dispatch = DingDingNoticeDispatch(s)
        s.pickle = DingDingPickle(s)
        s.censor = DingDingCensor(s)

        s.pickle.load()
    def run(s):
        while True:
            while select.select( [s.server],[],[], 0 )[0] != []:
                s.server.handle_request()
            s.work_orders.carry_on()
    def event_readfromdict( s, data_dict ):
        """
        Loading data from the data dictionary.
        """
        s.subscriptions.event_readfromdict( data_dict )
    def event_writetodict( s, data_dict ):
        """
        Writing data to the data dictionary.
        """
        s.subscriptions.event_writetodict( data_dict )

class DingDingWorkOrders:
    """
    Work orders - When DingDing receives a request to make a
    subscription, or to perform a notify, or whatever, it responds
    *right away*, and then carries out the work later. DingDing
    places the *highest* priority on responding to requests.
    It carries out the requests *later.*
    """
    def __init__( s, dingding ):
        s.dingding = dingding
        s.orders = [] # a list of (func, args) pairs
    def add_order( s, func, args ):
        """
        Add a (func,args) pair to the list of work orders.
        """
        s.orders.append( (func,args) )
    def any_orders(s):
        """
        Tell if there are any orders right now or no.
        """
        return len(s.orders)>0
    def carry_on(s):
        """
        Perform one work order.
        """
        if len(s.orders)==0:
            return
        (func,args)=s.orders.pop(0)
        func(*args)

class DingDingUli:
    """
    ULI = Universal Line Interface.
    
    Receives a string (a line,) and returns a string (possibly multi-line.)
    """
    def __init__( s, dingding ):
        s.dingding = dingding
    def uli( s, msg ):
        if msg == "ping": return "pong\n"
        elif msg == "whoareyou": return s.dingding.options.get_servertitle()+"\n"
        elif msg == "frametype": return "Custom frame - Ding Ding v5 HTTP Server.\n"
        elif msg == "whoareyou-data": return "nLSD description retrival not supported yet.\n"
        elif msg == "help": return "list-subscriptions, subscribe server-pw xmlrpc-url subs-pw, pnote server-pw note\n"
        elif msg == "list-subscriptions":
            visible = s.dingding.subscriptions.visible_by_permit( PUBLIC_PERMIT )
            return "Subscriptions: " + " ".join( [subs.title for subs in visible] ) + "\n"
        elif msg.startswith( "pnote" ):
            import shlex
            (cmd, server_pw, note) = shlex.split( msg,3 )
            dmsg = {"Action":"pnote", "Text":note, "TransparencyText":"pnote: %s" % note}
            dconn = {"WhoCanSeeThis":s.dingding.options.get_defaultmessagevisibility()}
            s.dingding.notice_dispatch.notify(dmsg, Connection(dconn, s.dingding))
            return "pnote sent"
        elif msg.startswith( "subscribe" ):
            
            import shlex
            (cmd, server_pw, xmlrpc_url, subscribers_pw) = shlex.split( msg )
            s.dingding.subscriptions.subscribe( Subscription( { "MatchPattern": ["ALL"],
                                                                "XmlRpcRecvUrl": xmlrpc_url,
                                                                "RecvPassword": subscribers_pw,
                                                                "Comment": "(connected via ULI)" },
                                                              s.dingding ),
                                                Connection( { "Password": server_pw }, s.dingding ) )
            return "(subscribing %s...)\n" % xmlrpc_url
        return "(I do not understand: %s)\n" % msg

class DingDingOptions:
    """
    Parses and keeps track of command-line options. Also, provides
    default values. Many other components reference this to figure
    out the configuration state.
    """
    def __init__( s, dingding ):
        s.dingding = dingding
        
        import optparse
        parser = optparse.OptionParser()

        server_notify_password = "password" # THIS MUST CHANGE TO A REQUIRED PARAMETER BY OPTPARSE!!!
        
        parser.add_option( "-H", "--host", dest="host_name", default="127.0.0.1",
                           type="string", help = "specify hostname to run on" )
        parser.add_option( "-p", "--port", dest="port_number", default=80,
                           type="int", help = "port number to run on" )
        parser.add_option( "-t", "--title", dest="title", default="DingDing V5 Event Server",
                           type="string", help = "title for the running event server" )
        parser.add_option( "-d", "--debug", action="store_true", default=False,
                           dest="debug", help = "turn on debug print statements" )
        parser.add_option( "-P", "--pickle", default = "dingding.p",
                           dest="pickle", type="string", help = "persistence pickle's filename" )

        parser.add_option( "-V", "--component-visibility", dest="component_visibility", default="PUBLIC",
                           type="string", help = """default visibility for components ("PUBLIC" or "ADMIN-ONLY" or a group-password)""" )
        parser.add_option( "-v", "--message-visibility", dest="message_visibility", default="PUBLIC",
                           type="string", help = """default visibility for messages ("PUBLIC" or "ADMIN-ONLY" or a group-password)""" )

        (options, args) = parser.parse_args()
        if options.component_visibility not in [ "PUBLIC", "ADMIN-ONLY" ]:
            options.component_visibility = [ options.component_visibility ] # group, so put in a list
        if options.message_visibility not in [ "PUBLIC", "ADMIN-ONLY" ]:
            options.message_visibility = [ options.message_visibility ] # group, so put in a list

        if len( args ) != 1:
            parser.error( "Server password is a required argument. List it first thing after 'python2.3 dingding.py'" )
        
        s.server_notify_password = args[0]
        s.options = options
    def get_hostname(s):
        return s.options.host_name
    def get_portnumber(s):
        return s.options.port_number
    def get_servertitle(s):
        return s.options.title
    def get_serverurl(s):
        return "http://%s:%s/" % (s.options.host_name,s.options.port_number)
    def get_picklefilename(s):
        return s.options.pickle
    def get_defaultcomponentvisibility(s):
        return s.options.component_visibility
    def get_defaultmessagevisibility(s):
        return s.options.message_visibility
    

class DingDingPickle:
    def __init__( s, dingding ):
        s.dingding = dingding
    def get_filename(s):
        return s.dingding.options.get_picklefilename()
    def load(s):
        try:
            data = pickle.load( open( s.get_filename() ) )
            s.dingding.event_readfromdict( data )
        except IOError:
            pass
    def save(s):
        data = {}
        s.dingding.event_writetodict( data )
        pickle.dump( data, open(s.get_filename(),"w") )

class DingDingSubscriptions:
    def __init__( s, dingding ):
        s.dingding = dingding
        s.subscriptions = []

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
        return s._custom_reduce(foo, [r]+list_[2:], early_exit, load)

    def _match(s, load, pattern):
        op = pattern[0].upper()
        if op == "ALL":
            return True
        elif op == "NOT":
            return not s._match(load, pattern[1])
        elif op == "AND":
            return s._custom_reduce(lambda x, y: x and y,
                                    pattern[1:], False, load)
        elif op == "OR":
            return s._custom_reduce(lambda x, y: x or y,
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

    def get_interested_subscribers(s, msg):
        return [x for x in s.subscriptions if s._match(msg, x.match_pattern)]

    def subscribe( s, subs, conn ):
        if not s.dingding.security.is_connection_okay( conn ):
            return False
        s.subscriptions.append( subs )
        s.dingding.work_orders.add_order( s.dingding.pickle.save, [] )
        notice_dict = { "Action": "subscribe",
                        "SubscriptionSystem": "DingDingV5",
                        "TargetName": s.dingding.options.get_servertitle(),
                        "TargetUrl": s.dingding.options.get_serverurl(),
                        "TargetXmlRpc": s.dingding.options.get_serverurl(),
                        "SubscriberXmlRpc": subs.xmlrpc_recv_url, # required subscriber info
                        "MatchPattern": subs.match_pattern
                        }
        if subs.title: notice_dict[ "SubscriberName" ] = subs.title
        if subs.url: notice_dict[ "SubscriberUrl" ] = subs.url
        s.dingding.work_orders.add_order( s.dingding.notice_dispatch.notify, [notice_dict, conn] )
    def visible_by_permit( s, permit ):
        return [subs for subs in s.subscriptions if s.dingding.censor.is_this_visible( permit, subs )]
    def event_readfromdict( s, data_dict ):
        """
        Loading data from the data dictionary.
        """
        print data_dict[ "subscriptions" ]
        s.subscriptions = [ Subscription( subscription_dictionary, s.dingding ) for subscription_dictionary in data_dict[ "subscriptions" ] ]
        print s.subscriptions
    def event_writetodict( s, data_dict ):
        """
        Writing data to the data dictionary.
        """
        data_dict[ "subscriptions" ] = [subs.subscription_dictionary for subs in s.subscriptions]

class DingDingNoticeDispatch:
    """
    Dispatches notice that an event has happened.

    It works with the subscriptions list to find matches for a message.
    Then it checks with the confidentiality module to filter out
    subscribers that aren't authorized to receive the notice.

    It then notifies each valid recipient of the notice.
    """
    def __init__( s, dingding ):
        s.dingding=dingding

    def notify( s, notice_dict, conn ):
        """
        Go to subscriptions and get list of interested subscriptions
        Go to confidentiality module and weed out subscriptions not authorized
        Send out notice to remaining subscriptions

        Not addressed:
           Microservers don't receive notice
           Does notcurrently use Futures
           Reporting bad subscriptions
        """
        subs = s.dingding.subscriptions.get_interested_subscribers(notice_dict)
        subs = [x for x in subs if s.dingding.censor.is_this_visible(x.get_permit(), conn)]
        targets = [(x.xmlrpc_recv_url,x.recv_password) for x in subs]
        unique_targets = []
        for x in targets:
            if x not in unique_targets:
                unique_targets.append(x)
        for (URL, pw) in unique_targets:
            server=xmlrpclib.ServerProxy(URL)
            d = {}
            if pw!=None:
                d["Password"] = pw
            result = server.notify(notice_dict,d)

class DingDingSecurity:
    def __init__( s, dingding ):
        s.dingding = dingding
    def is_connection_okay( s, conn ):
        pw = s.dingding.options.server_notify_password
        return conn.is_password( pw )

class DingDingCensor:
    def __init__( s, dingding ):
        s.dingding = dingding
    def is_this_visible( s, permit, subs ):
        if permit.is_admin():
            return True # admin can see anything
        if subs.who_can_see_this == "PUBLIC":
            return True # anyone can see what is public
        if type(subs.who_can_see_this) == type([]):
            for group_pw in permit.groups():
                if group_pw in subs.who_can_see_this:
                    return True # group_pw matches visibility password
        return False # otherwise, not allowed to see

class DingDingHttpServer( BaseHTTPServer.HTTPServer ):
    """
    Receives events, hands them off to the DingDingHttpHandler.
    The DingDingHttpServer also helps the DingDingHttpHandler
    find the DingDing instance.
    """
    def __init__( s, dingding ):
        s.dingding = dingding
        hostname = s.dingding.options.get_hostname()
        portnum = s.dingding.options.get_portnumber()
        BaseHTTPServer.HTTPServer.__init__( s, (hostname,portnum), DingDingHttpHandler )

class DingDingHttpHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header( "Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        s.do_HEAD()
        s.wfile.write( "<html><head><title>Nothing Yet</title></head><body><p>Work in progress! DingDing v5.</p></body></html>" )
    def do_POST(s):
        s.do_HEAD()
        clen = int( s.headers.getheader( "content-length" ) )
        body = s.rfile.read( clen )
        d = cgi.parse_qs( body )
        try:
            uli_string = d.get( "ULI", d.get( "uli", d.get( "Uli", [None] )))[0]
        except KEYERROR:
            uli_string = None
        try:
            (args,func_name) = xmlrpclib.loads( body )
            s.wfile.write( xmlrpclib.dumps( (1,) ) ) # auto response, for now
            if func_name == "subscribe":
                s.handle_xmlrpc_subscribe( *args )
        except ExpatError:
            pass
        if uli_string != None:
            s.wfile.write( s.server.dingding.uli.uli( uli_string ) )
            return
    def handle_xmlrpc_subscribe( s, subscription_dict, connection_dict ):
        """
        XML-RPC interface to subscription.
        Returns 0 if password doesn't check out.
        Returns 1 otherwise.
        """
        subs = Subscription( subscription_dict, s.server.dingding )
        conn = Connection( connection_dict, s.server.dingding )
        if not s.server.dingding.security.is_connection_okay( conn ):
            return 0
        s.server.dingding.work_orders.add_order( s.server.dingding.subscriptions.subscribe, [subs,conn] )
        return 1



if __name__ == "__main__":
    dd = DingDing()
    dd.run()
