import math
import struct
from cuckoo.filter import CuckooFilter
import bitarray
import time
import sys
import dynamic_dns

CAPACITY = 1479000
ERROR_RATE = 0.003
BUCKET_SIZE = 4
ZONE = ".cf.example.com"

# Initialize the Cuckoo Filter
cuckoo = CuckooFilter(capacity = CAPACITY, error_rate = ERROR_RATE, bucket_size = BUCKET_SIZE)

fingerprint_size = int(math.ceil(math.log(1.0 / ERROR_RATE, 2) + math.log(2 * BUCKET_SIZE, 2)))

# Open the zone file of the DNS zone to parse
zone = open("/root/dnspriv/zone_files/ru.zone", "r")

cuckoo_initialization_start_time = time.time()
# Load the FQDNs from the zone file
fqdns = set()
for fqdn in zone:
    fqdn = fqdn.rstrip()
    fqdn = fqdn.split("\t")[0].split(" ")[0]
    fqdns.add(fqdn.lower())

# Load the FQDNs of the monitored zone in the Cuckoo Filter
for fqdn in fqdns:
    cuckoo.insert(fqdn)
cuckoo_initialization_end_time = time.time()
cuckoo_initialization_time = cuckoo_initialization_end_time - cuckoo_initialization_start_time
print(cuckoo_initialization_time)

# Make the changes in the Cuckoo Filter from the journalfile
changes_inclusion_start_time = time.time()
changesList = dynamic_dns.getDynamicChanges()
for item in changesList:
    name = item[0] + "."
    action = item[1]
    if action == "del":
        cuckoo.delete(name)
    if action == "add":
        cuckoo.insert(name)
changes_inclusion_end_time = time.time()
print("Changes incorporated for Cuckoo Filter in: ", changes_inclusion_end_time - changes_inclusion_start_time)
