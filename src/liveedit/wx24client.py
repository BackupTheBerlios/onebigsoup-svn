import xmlrpclib
import time
import difflib
import threading

from wxPython.wx import *
from wxPython.xrc import *



GUI_FILENAME       = "wxclient.xrc"
GUI_MAINFRAME_NAME = "LiveEditFrame"

LIVEEDIT_SERVER_XMLRPC_URL = "http://services.taoriver.net:9021/"
#LIVEEDIT_SERVER_XMLRPC_URL = "http://shazbot.screwedup.org:9500/"

THREAD_SLEEP_TIME = 3.0 # 3 seconds



SWITCH_PUSH = "push"
SWITCH_NEUTRAL = "neutral"
SWITCH_PULL = "pull"

THREAD_ASLEEP = "asleep"
THREAD_AWAKE = "awake"


class LiveEditApp( wxApp ):
    """

    Live shared editing application.

  Things we care about:
  * Thread - performing XML-RPC calls, once every 3 seconds
  * User Interface - talks with user, can't thread
  * Switch - an FSM with states PUSH, PULL, and NEUTRAL
  * Outgoing - Holds outgoing messages,
               buffers User Interface from threading.
  * Incoming - Holds incoming messages,
               buffers User Interface from threading

  How information cycles about:

       .---->---- Push Buffer ------->----------.
       |                                        |
       |   (keystrokes)---v                     |
    User                PUSH   <..              |
  Interface           NEUTRAL  <--SWITCH     Thread  <---network--->  Server
       |                PULL   <''              |
       |                  ^-------(retrievals)  |
       |                                        |
       '----<---- Pull Buffer -------<----------'

  The Thread and the User Interface coordinate with the Switch:
  
  States:
  * PUSH:    Going to upload info, clobbering whatever's on the server.
  * PULL:    There's some data waiting from the server, waiting to
             clobber the User Interface.
  * NEUTRAL: The user hasn't typed yet, and there's no data waiting
             from the server.

  The Switch's state diagram:
  
      .---<--- PUSH ---<---.
      |                    |
   Thread                 UI             (i.e., User
   picked up           deposited            Typed
   Push buffer       into Push buffer     Something)
      |                    |
      +--->-- NEUTRAL -->--+
      |                    |
     UI                 Thread
  picked up           deposited
 pull buffer       into Pull buffer
      |                    |
      '---<--- PULL ---<---'
    """
    
    def init_gui(s):
        """
        Load the XML User Interface description (XRC) file,
        and locate the user interface widgets we'll need.
        """
        s.res   = wxXmlResource( GUI_FILENAME )
        s.frame = s.res.LoadFrame( None, GUI_MAINFRAME_NAME )
        s.load_btn = XRCCTRL( s.frame, "Load" )
        EVT_BUTTON( s.frame, XRCID( "Load" ), s.load )
        s.save_btn = XRCCTRL( s.frame, "Save" )
        EVT_BUTTON( s.frame, XRCID( "Save" ), s.save )
        s.pagename_ctrl = XRCCTRL( s.frame, "PageName" )
        s.pagetext_ctrl = XRCCTRL( s.frame, "PageText" )
        EVT_TEXT( s.frame, XRCID( "PageText" ), s.user_typed )
        EVT_IDLE( s.frame, s.idle_event )
        s.frame.Show(1)
        s.working_in_pagetext = False

    def init_server_relations(s):
        """
        Keep a pointer to the document server,
        and start keeping track of traffic.
        """
        s.server = xmlrpclib.ServerProxy( LIVEEDIT_SERVER_XMLRPC_URL )

        s.last_received_page_name = None
        
        # ----- new threading stuff
        s.push_buffer = None
        
        s.pull_buffer = None
        s.new_page_name = None  # a pull buffer, used when we opening a page
        
        s.switch_state = SWITCH_NEUTRAL
        s.thread_state = THREAD_ASLEEP
        s.thread = threading.Thread( target=s.thread_loop )
        s.thread.start()
        
    def OnInit( s ):
        """
        Initialize the GUI,
        start relations with the doc server,
        and perform a first fetch.
        """
        s.init_gui()
        s.init_server_relations()
        return 1

    def thread_loop(s):
        """
        Runs forever, in a while True loop,
        talking with the network periodically to either PUSH or PULL.

        Initially invoked in OnInit for the Client.

        If the switch is...
        PUSH:
          1. copy outgoing buffer to own variable.
          2. flip switch to NEUTRAL
               - We do this now, so that if the user types,
                 we'll get to it next time.
          3. post to doc server

        PULL or NEUTRAL:
          1. get update from document server
          2. store in incoming buffer
          3. flip switch to PULL
        """
        while True:
            s.thread_state = THREAD_AWAKE
            # check switch
            # do stuff, make appropriate calls...
            if s.switch_state == SWITCH_PUSH:
                push_buffer = s.push_buffer # thread's reference
                s.switch_state = SWITCH_NEUTRAL
                s.server.post_update( push_buffer )
            elif s.switch_state in [SWITCH_NEUTRAL, SWITCH_PULL]:
                # perform call
                d = s.server.get_update()
                # set buffers
                if d["page_name"] != s.last_received_page_name:
                    s.new_page_name = d["page_name"]
                    s.last_received_page_name = d["page_name"]
                s.pull_buffer = d["page_text"]
                s.switch_state = SWITCH_PULL
            else:
                raise "Should never happen."
            
            # sleep for three seconds
            s.thread_state = THREAD_ASLEEP
            time.sleep(THREAD_SLEEP_TIME)

    def adjust_text_control_contents( s, text ):
        """
        Use diffs to change the text control's
        contents to match the given string.
        """
        s.working_in_pagetext = True
        pos = s.pagetext_ctrl.GetInsertionPoint()
        
        old_text = s.pagetext_ctrl.GetValue()
        new_text = text
        matcher = difflib.SequenceMatcher( a=old_text,
                                           b=new_text )
        commands = matcher.get_opcodes()
        commands.reverse()
        for (op,a1,a2,b1,b2) in commands:
            print op,a1,a2,b1,b2
            if op == "replace":
                s.pagetext_ctrl.Replace( a1,a2, new_text[b1:b2] )
            elif op == "delete":
                s.pagetext_ctrl.Remove( a1,a2 )
            elif op == "insert":
                # I hope this doesn't delete a character inappropriately..
                # alternative:

                # is this the problem?
                s.pagetext_ctrl.SetInsertionPoint(a1)
                s.pagetext_ctrl.WriteText( new_text[b1:b2] )
                #s.pagetext_ctrl.Replace( a1,a1, new_text[b1:b2] )
            elif op == "equal":
                pass
            else:
                raise "Should Never Happen"
        
        s.pagetext_ctrl.SetInsertionPoint( pos )
        s.working_in_pagetext = False
    
    def idle_event(s,evt):
        """
        If the thread's pulled some data for us,
        read it out!
        """
        print "Idle event."
        if s.switch_state != SWITCH_PULL:
            return
        print "Fetching"
        if s.new_page_name != None:
            print "New Name"
            # New page: Overhaul everything
            s.working_in_pagetext = True
            s.pagetext_ctrl.SetValue( s.pull_buffer )
            s.pagename_ctrl.SetValue( s.new_page_name )
            s.working_in_pagetext = False
            s.new_page_name = None
            s.switch_state = SWITCH_NEUTRAL
            return
        print "Old Name"
        text = s.pull_buffer
        s.adjust_text_control_contents( text )
        s.switch_state = SWITCH_NEUTRAL
        return
    
    def load(s, evt):
        # wait for thread to fall asleep
        while s.thread_state == THREAD_AWAKE:
            pass

        # call server
        d = s.server.load_page( s.pagename_ctrl.GetValue() )
        s.working_in_pagetext = True
        s.pagetext_ctrl.SetValue( d[ "page_text" ] )
        s.working_in_pagetext = False
        s.switch_state = SWITCH_NEUTRAL
    
    def save(s, evt):
        # wait for thread to fall asleep
        while s.thread_state == THREAD_AWAKE:
            pass
        
        # call server, posting latest version, and saving
        s.server.save_page( s.pagetext_ctrl.GetValue() )

    def user_typed(s, evt):
        s.push_buffer = s.pagetext_ctrl.GetValue()
        s.switch_state = SWITCH_PUSH


if __name__ == '__main__':
    app = LiveEditApp()
    app.MainLoop()


