all_lists = []

PermReadWrite = 1
PermReadOnly = 0

uli_int = int

def new_list():
    all_lists.append([PermReadWrite])
    return len(all_lists)-1

def cap_list(n):
    all_lists[n][0] = PermReadOnly
    return n

def open_list(n):
    all_lists[n][0] = PermReadWrite
    return n

def add_to_list(n, s):
    all_lists[n].append(s)
    return n

def uli(line):
    cmd = line.split(" ", 1)
    if len(cmd) == 0:
        return "wtf, mate?"
    cmd[0] = cmd[0].lower()
    if cmd[0] == "help":
        return "DON'T PANIC"
    elif cmd[0] == "new":
        n = new_list()
        return "List created: #%d" % (n)
    elif cmd[0] == "cap":
        n = uli_int(cmd[1])
        cap_list(n)
        return "List capped: #%s" % (n)
    elif cmd[0] == "open":
        n = uli_int(cmd[1])
        open_list(n)
        return "List opened: #%d" % (n)
    elif cmd[0] == "add":
        cmdR = cmd[1].split(" ", 1)
        add_to_list(uli_int(cmdR[0]), cmdR[1])
        return "Added"
    elif cmd[0] == "regurgitate":
        s = ""
        for x in all_lists[uli_int(cmd[1])][1:]:
            s = s + x + "\n"
        return s.strip()



#def main():
#    while True:
#        print uli_dwim(raw_input(">>> "))

if __name__ == "__main__":
    import http_server
    
    http_server.run( "ULI List Server",
                     "services.taoriver.net", 9302,
                     uli_func=uli )
