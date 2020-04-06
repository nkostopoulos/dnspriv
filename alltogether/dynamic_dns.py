import os
import subprocess
from cuckoo.filter import CuckooFilter

ZONE = "cf4.example.com"
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
    #command_syncDynDNS = "rndc sync -clean"
    #os.system(command_syncDynDNS)
    
    # Find the distinct names from the journal file and their most recent action
    journal = journal.split(b"\n")
    distinct_names = dict()
    if journal == [b'']:
        return None
    for line in journal:
        items = line.split(b"\t")
        first_two = items[0].split(b" ")
        action = first_two[0]
        name = first_two[1]
        name = name[:-1]
        if name in distinct_names.keys():
            if distinct_names[name] == "del" and action == "add":
                distinct_names.pop(name, None)
        else:
            distinct_names[name] = action

    return distinct_names

if __name__ == "__main__":
    getDynamicChanges()
