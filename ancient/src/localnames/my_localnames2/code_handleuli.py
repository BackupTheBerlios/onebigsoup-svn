LN_HELP="ln (space) (name) (url), pickle, space-notes"


def uli_ln( msg ):
    import code_info
    parts = msg.split()
    if len(parts) < 3:
        return "format:  " + LN_HELP
    space=parts[0].upper()
    names=[parts[1]]
    url=parts[2]
    names.extend( parts[3:] )
    code_info.add_new_names( space, names, url )
    return "added"

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
    parts = msg.split(None,1)
    if len(parts)==2:
        (first,rest) = parts
        first = first.lower()
        if first == "ln":
            return uli_ln( rest )
        if first == "pickle":
            import code_old
            return code_old.hub.pickle.uli( rest )
        if first == "space-notes":
            import code_old
            return code_old.hub.space_notes.uli( rest )
    return "not understood"
