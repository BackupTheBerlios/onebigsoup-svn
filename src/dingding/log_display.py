"""
log_display module

PLEASE KEEP CODE PYTHON 2.2 COMPATIBLE!

This code displays collections of log entries.

Many programs need to draw collections of logs.
This is some convenient code that will do it for you.
"""

import pprint

NULL_TIME = "0000-00-00T00:00:00"

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;" }

def html_escape( text ):
    l=[]
    for c in text:
        l.append( html_escape_table.get(c,c) )
    return "".join(l)

content_type = {
    "text": "text/plain",
    "raw":  "text/plain",
    "rss":  "application/rss+xml",
    "html": "text/html",
    }



def sort_logs( logs ):
    """
    Yes, you can do this shorter with Python2.3.
    We're trying to keep it Python2.2 compatible, for now.
    """
    decorated = []
    for log in logs:
        decorated.append( (log.get( "TimeEventHappened",
                                    NULL_TIME ),
                           log) )
    decorated.sort()
    decorated.reverse()
    sorted = []
    for (time,log) in decorated:
        sorted.append( log )
    return sorted



def tuple_from_iso8601( iso8601 ):
    return time.strptime( iso8601.replace("-",""), "%Y%m%dT%H:%M:%S" )

def iso8601_from_tuple( tuple_time ):
    return time.strftime( "%Y-%m-%dT%H:%M:%S", tuple_time )

def hour_and_ampm( tuple_time ):
    return time.strftime("%I %p", tuple_time)

def dayname( tuple_time ):
    """
    In Python2.3, you can do this with the datetime module.
    But we want to keep Python2.2 compatible.
    """
    day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    return day_names[ tuple_time[6] ]



def as_text( logs ):
    """
    Returns TransparencyText of logs.
    """
    l=[]
    
    for log in logs:
        timestamp = log.get( "TimeEventHappened",
                             NULL_TIME )
        if len(timestamp)>len(NULL_TIME):
            timestamp = timestamp[:len(NULL_TIME)]
        print timestamp, str(type(timestamp))
        l.append( timestamp + " " + log.get("TransparencyText",
                                            "(no self-description)")+"\n" )
    return "".join(l)

def as_raw( logs ):
    """
    Returns text representation of logs as Python dictionaries.
    """
    l=[]
    for log in logs:
        l.append( pprint.pformat( log )+"\n" )
    return "".join(l)



def as_rss( logs, title, link, description, language="en-us" ):
    l=[]
    l.append( """<?xml version="1.0" encoding="ISO-8859-1" ?>
 <rss version="0.91">

 <channel>
 <title>%(title)s
 <link>%(link)s</link>
 <description>%(description)s</description>
 <language>%(language)s</language>
 """ % vars() )
    for log in logs:
        l.append( "<item>\n" )
        l.append( "<title>%s</title>\n" % log.get("TransparencyText",
                                                  "(no self-description") )
        l.append( "<description>\n" )
        l.append( html_escape(pprint.pformat(log))+"\n" )
        l.append( "</description>\n" )
        l.append( "</item>\n" )
    l.append( "</channel>\n" )
    l.append( "</rss>\n" )
    return "".join( l )


def row_in_html( row ):
    """
    row: list of strings
    """
    return "<tr><td>" + "</td><td>".join( row ) + "</td></tr>"
def row_in_html_bold( row ):
    """
    row: list of strings
    """
    return "<tr><td><b>" + "</b></td><td><b>".join( row ) + "</b></td></tr>"

class SingleTableWriter:
    """
    Collects details for a single table,
    and writes them out.
    """
    def __init__( s, row_headers=None ):
        """
        row_headers: list of strings
        """
        s.headers = row_headers
        s.rows = []
    def row_headers(s):
        return s.headers
    def add_row( s, row_data ):
        """
        row_data: list of strings
        """
        s.rows.append( row_data )
    def as_html(s):
        html=[]
        html.append( "<table>\n" )
        if s.headers != None:
            html.append( row_in_html_bold(s.headers)+"\n" )
        for row in s.rows:
            html.append( row_in_html(row)+"\n" )
        html.append( "</table>\n" )
        return "".join(html)
    
class MultiTableWriter:
    """
    Provide entries, with optional headers.
    TableWriter will create an HTML table
    for each collection of rows that
    share the same headers.
    """
    def __init__(s):
        s.cur_table = None
        s.l = []
    def add_row( s, data, headers=None ):
        # if the headers is the same, contribute to the same table.
        # if the headers are different, close off one table,
        # and begin the next.
        if s.cur_table == None:
            s.cur_table = SingleTableWriter( headers )
        elif s.cur_table.row_headers() != headers:
            s.l.append( s.cur_table.as_html() )
            s.cur_table = SingleTableWriter( headers )
        s.cur_table.add_row( data )
    def flush(s):
        if s.cur_table != None:
            s.l.append( s.cur_table.as_html() )
        s.cur_table = None
    def as_html(s):
        s.flush()
        return "".join(s.l)

def as_html(logs):
    tables = MultiTableWriter()
    
    for log in logs:
        if log.has_key( "TransparencyXhtmlColumnHeaders" ) and log.has_key( "TransparencyXhtmlRow" ):
            escaped_headers = []
            for item in log["TransparencyXhtmlColumnHeaders"]:
                escaped_headers.append( html_escape(item) )
            tables.add_row( log["TransparencyXhtmlRow"],
                            escaped_headers )
        elif log.has_key( "TransparencyXhtml" ):
            tables.add_row( [log["TransparencyXhtml"]], None )
        elif log.has_key( "TransparencyText" ):
            tables.add_row( [log["TransparencyText"]], None )
        else:
            tables.add_row( ["(no self-description)"], None )
    return tables.as_html()

def as_html_with_day_display(logs):
    tables = MultiTableWriter()

    last_day_displayed = None

    for log in logs:
        time_event_happened = log.get( "TimeEventHappened",
                                       NULL_TIME )
        tuple_time = tuple_from_iso8601( time_event_happened )
        
        day_string = dayname( tuple_time )
        hour_ampm_string = hour_and_ampm( tuple_time )
        
        escaped_headers = ["time"] # will be extended
        row_data = [time_event_happened] # will be extended

        if log.has_key( "TransparencyXhtmlColumnHeaders" ) and log.has_key( "TransparencyXhtmlRow" ):
            for item in log["TransparencyXhtmlColumnHeaders"]:
                escaped_headers.append( html_escape(item) )
            row_data.extend( log["TransparencyXhtmlRow"] )
        elif log.has_key( "TransparencyXhtml" ):
            escaped_headers.append( "data" )
            row_data.append( log["TransparencyXhtml"] )
        elif log.has_key( "TransparencyText" ):
            escaped_headers.append( "data" )
            row_data.append( html_escape(log["TransparencyText"]) )
        else:
            escaped_headers.append( "data" )
            row_data.append( "(no self-description)" )
        tables.add_row( row_data, escaped_headers )
    return tables.as_html()
