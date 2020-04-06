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
zone = open("./ru.zone", "r")

# Load the FQDNs from the zone file
fqdns = set()
for fqdn in zone:
    fqdn = fqdn.rstrip()
    fqdn = fqdn.split("\t")[0].split(" ")[0]
    fqdns.add(fqdn.lower())

cuckoo_initialization_start_time = time.time()
# Load the FQDNs of the monitored zone in the Cuckoo Filter
for fqdn in fqdns:
    cuckoo.insert(fqdn)
cuckoo_initialization_end_time = time.time()
cuckoo_initialization_time = cuckoo_initialization_end_time - cuckoo_initialization_start_time
print(cuckoo_initialization_time)

# make sure that the names that will be deleted are in the Cuckoo Filter
changes_dict = dynamic_dns.getDynamicChanges()
for key in changes_dict:
    if changes_dict[key].decode("utf-8") == "del":
        cuckoo.insert(key.decode("utf-8"))

# Make the changes in the Cuckoo Filter from the journalfile
changes_inclusion_start_time = time.time()
changes_dict = dynamic_dns.getDynamicChanges()
for key in changes_dict:
    if changes_dict[key].decode("utf-8") == "del":
        cuckoo.delete(key.decode("utf-8"))
    if changes_dict[key].decode("utf-8") == "add":
        cuckoo.insert(key.decode("utf-8"))
changes_inclusion_end_time = time.time()
print("Changes incorporated for Cuckoo Filter in: ", changes_inclusion_end_time - changes_inclusion_start_time)

zone_file_creation_start_time = time.time()
filter_items_number = 0
cuckoo_contents = cuckoo.export()
contents_hex = list()
for bucket in cuckoo_contents:
    alist = list()
    for item in bucket:
        this = hex(int(item.to01(),2)).split('x')[-1]
        if int(this, 16) < 16:
            this = "00" + this
        elif int(this, 16) < 256:
            this = "0" + this
        else:
            pass
        alist.append(this)
        filter_items_number += 1
    contents_hex.append(alist)

# Populate zone with the metadata
RR1_2 = "capacity" + ZONE + " IN TXT " + str(CAPACITY)
RR2_2 = "buckets" + ZONE + " IN TXT " + str(BUCKET_SIZE)
RR3_2 = "fingerprint" + ZONE + " IN TXT " + str(fingerprint_size)

RRs_2nd = list()
for index in range(0, CAPACITY):
    RR = str(index) + ZONE + " IN TXT "
    RR_temp = str()
    for item in contents_hex[index]:
        RR_temp += item
    RR += RR_temp
    if RR_temp == "":
        RR += "."
    if len(contents_hex[index]) < 4:
        RRs_2nd.append(RR_temp + ".")
    else:
        RRs_2nd.append(RR_temp)

if fingerprint_size <= 4:
    fp_zone_file = 1
elif fingerprint_size <= 8:
    fp_zone_file = 2
elif fingerprint_size <= 12:
    fp_zone_file = 3
else:
    fp_zone_file = 4

STEP = int(256 / (fp_zone_file * BUCKET_SIZE))
# 2nd: Create Cuckoo Filter zone with each RR corresponding to multiple buckets
current_RR = str()
current_RR_size = 0
current_RR_sequence = 0
RRs_2nd_configured = list()
for item in RRs_2nd:
    if current_RR_size < STEP:
        current_RR += item
        current_RR_size += 1
    else:
        RR = str(current_RR_sequence) + ZONE + " IN TXT " + current_RR
        RRs_2nd_configured.append(RR)
        current_RR = str()
        current_RR_size = 0
        current_RR_sequence += 1

file_2nd = open("./file_2nd", "w")
file_2nd.write(RR1_2 + "\n")
file_2nd.write(RR2_2 + "\n")
file_2nd.write(RR3_2 + "\n")
for line in RRs_2nd_configured:
    file_2nd.write(line + "\n")
zone_file_creation_end_time = time.time()
print("Zone File Created in: ", zone_file_creation_end_time - zone_file_creation_start_time)
