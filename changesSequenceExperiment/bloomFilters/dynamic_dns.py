import os
import subprocess
from cuckoo.filter import CuckooFilter

ZONE = "cf3.example.com"
JOURNAL = "/etc/bind/" + ZONE + ".jnl"

CAPACITY = 85
ERROR_RATE = 0.003
BUCKET_SIZE = 4

cuckoo = CuckooFilter(capacity = CAPACITY, error_rate = ERROR_RATE, bucket_size = BUCKET_SIZE)

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
    for line in journal:
        items = line.split(b"\t")
        first_two = items[0].split(b" ")
        action = first_two[0]
        name = first_two[1]
        distinct_names[name] = action

    return distinct_names

    # Iterate over keys in the dictionary and add them in the Cuckoo Filter
    #for key in distinct_names:
        #print(key.decode("utf-8"), distinct_names[key].decode("utf-8"))
        #fingerprint, indices = cuckoo.get_fingerprint(key)
        #for index in indices:
            #print(index)

if __name__ == "__main__":
    getDynamicChanges()
