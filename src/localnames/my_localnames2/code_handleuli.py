LN_HELP="ln (space) (name) (url)"

def uli( msg ):
    if msg.lower() == "ping":
        return "pong"
    if msg.lower() == "whoareyou":
        return "my.localnames server"
    if msg.lower() == "frametype":
        return "custom"
    if msg.lower() == "whoareyou-data":
        return "nLSD description retrival not supported yet."
    if msg.lower() == "help":
        return LN_HELP
    parts = msg.split()
    if parts[0].lower() == "ln":
        import code_info
        if len(parts) < 4:
            return "format:  " + LN_HELP
        space=parts[1].upper()
        names=[parts[2]]
        url=parts[3]
        names.extend( parts[4:] )
        code_info.add_new_names( space, names, url )
        return "added"
    
    return "not understood"
