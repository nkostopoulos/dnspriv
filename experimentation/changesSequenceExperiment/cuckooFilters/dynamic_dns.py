import os
import subprocess
from cuckoo.filter import CuckooFilter

ZONE = "ru"
JOURNAL = "/etc/bind/" + ZONE + ".jnl"

def save_output(command):
    proc = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
    (out, err) = proc.communicate()
    return out.rstrip(b'\n')

def getDynamicChanges():
    # Temporarily disable Dynamic DNS for monitored zone
    command_stopDynDNS = "rndc freeze " + ZONE
    os.system(command_stopDynDNS)

    # Print the journal of the monitored Dynamic DNS zone
    command_getJournal = "named-journalprint " + JOURNAL + " | grep -v 'SOA'"
    journal = save_output(command_getJournal)

    # Enable Dynamic DNS for monitored zone
    command_restartDynDNS = "rndc thaw " + ZONE
    os.system(command_restartDynDNS)
    
    # Sync Dynamic DNS zone and clean journal
    command_syncDynDNS = "rndc sync -clean"
    os.system(command_syncDynDNS)
    
    # Collect the names from the journalfile. Two important points
    # 1: Names whose value was just updated, i.e. del and then add actions will be skipped
    # 2: One FQDN may correspond to different RRs (different values, different TTL, different RR type)
    journal = journal.split(b"\n")
    actionDict = dict()
    changesList = list()
    if journal == [b'']:
        return None
    for line in journal:
        items = line.split(b"\t")
        action_and_name = items[0].split(b" ")
        action = action_and_name[0]
        name = action_and_name[1]
        ttl = items[1]
        rrType = items[3]
        name = name[:-1]
        if (name, ttl, rrType) in actionDict.keys():
            if actionDict[(name, ttl, rrType)] == b"del" and action == b"add":
                actionDict.pop((name, ttl, rrType), None)
                changesList.remove((name.decode("utf-8"), action.decode("utf-8")))
            else:
                changesList.append((name.decode("utf-8"), action.decode("utf-8")))
        else:
            actionDict[(name, ttl, rrType)] = action
            changesList.append((name.decode("utf-8"), action.decode("utf-8")))

    return changesList

if __name__ == "__main__":
    getDynamicChanges()
