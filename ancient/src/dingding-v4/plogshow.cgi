#!/usr/bin/python
print "Content-Type: text/html\n\n"

import time, plogtalk, socket

def get_wiki_logs():
    # get 3 days worth of logs
    server = plogtalk.PlogServer( "http://plog.taoriver.net:8000/" )
    LionKimbro = server.user( "LionKimbro" )
    logs = LionKimbro.get_logs( "wikipost", maxnum=20, maxage=3*24*60*60 )
    return logs

def hour_and_ampm( seconds_since_epoch ):
    tuple_time = time.localtime( seconds_since_epoch )
    return time.strftime("%I %p", tuple_time)

def dayname( seconds_since_epoch ):
    tuple_time = time.localtime( seconds_since_epoch )
    day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    return day_names[ tuple_time[6] ]

def print_wiki_logs_head():
    print """
<h3>Wiki Plogs</h3>
All times local to Seattle, WA. Last 3 days.
<table>
<tr><td></td><td><b>wiki:page</b></td><td><b>commit comment</b></td></tr>
"""

def print_wiki_logs_tail():
    print "</table>"
    print

def print_wiki_row( log ):
       print "<tr>"
       print "<td>%s</td>" % hour_and_ampm( log["time"] )
       print """<td><a href="%(WikiURL)s">%(InterWikiName)s</a>:""" % log
       print """<a href="%(PageURL)s">%(PageName)s</a></td>""" % log
       print """<td>%(Comment)s</td>""" % log
       print "</tr>"

def print_wiki_logs( logs ):
    last_day_printed = None
    logs.reverse() # most recent at top
    print_wiki_logs_head()
    for log in logs:
        cur_day = dayname( log["time"] )
        if cur_day != last_day_printed:
            last_day_printed = cur_day
            print """<tr class="dayname"><td>%s</td></tr>""" % cur_day
	print_wiki_row( log )
    print_wiki_logs_tail()

def if_logs_show_them():
    logs = get_wiki_logs()
    if len( logs ) == 0:
      return
    print_wiki_logs( logs )

top = """
<html>
<head>
<title>Lion Kimbro - Recent Activity</title>
<style type="text/css">
<!--
BODY { color: #000000;
       background-color: #ffffff }

H1 { text-align: center;
     color: yellow;
     background-color: black }

H3 { background-color: #aaaaff }

H4 { background-color: #aaffff }

IMG.Portrait { border: 3px solid #000000 }

P.TagLine { text-align: right }

CODE {
color: #300070;
}

PRE {
color: #300070;
margin: 0 15px 0 15px;
padding: 5px;
border: dotted 1px #0000FF;
}

td {
border: 1px solid #EEEEEE;
}
-->
</style>
</head>
<body>
<h1>Lion Kimbro - Recent Activity</h1>

"""

bottom = """
</body>
</html>
"""

print top
try:
    if_logs_show_them()
except socket.error:
    print "<p>Plog server down.</p>"
print bottom
