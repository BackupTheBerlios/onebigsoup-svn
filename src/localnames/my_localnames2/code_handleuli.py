

def uli( msg ):
    if msg == "ping":
        return "pong"
    if msg == "whoareyou":
        return "my.localnames server"
    if msg == "frametype":
        return "custom"
    if msg == "whoareyou-data":
        return "nLSD description retrival not supported yet."
    if msg == "help":
        return "This is the ULI interface to the my.localnames server. Not much here, at the moment."
    return "not understood"
