import math
import struct
from cuckoo.filter import CuckooFilter
import bitarray

CAPACITY = 2305
ERROR_RATE = 0.003
BUCKET_SIZE = 4
ZONE1 = ".hz.tld."
ZONE2 = ".hz.tld."

# Initialize the Cuckoo Filter
cuckoo = CuckooFilter(capacity = CAPACITY, error_rate = ERROR_RATE, bucket_size = BUCKET_SIZE)

fingerprint_size = int(math.ceil(math.log(1.0 / ERROR_RATE, 2) + math.log(2 * BUCKET_SIZE, 2)))

# The DNS zone to parse (netmode.ece.ntua.gr)
zone = open("/root/dnspriv/zone_files/ntua_names", "r")

fqdns = set()
for item in zone:
    item = item.rstrip()
    fqdn = item.split("\t")[0].split(" ")[0]
    fqdns.add(fqdn.lower())

# Find the number of distinct FQDNs in the zone netmode.ece.ntua.gr
number_of_fqdns = len(fqdns)
print("Number of Distinct FQDNs in ntua zone: ", number_of_fqdns)

load_factor = number_of_fqdns / (CAPACITY * BUCKET_SIZE)
print("Load factor: ", load_factor)

# Load the FQDNs of the monitored zone in the Cuckoo Filter
for fqdn in fqdns:
    cuckoo.insert(fqdn)

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

print(contents_hex)

print("Number of items stored in the filter: ", filter_items_number)

# Populate zone with the metadata
RR1_1 = "capacity" + ZONE1 + " IN TXT " + str(CAPACITY)
RR2_1 = "buckets" + ZONE1 + " IN TXT " + str(BUCKET_SIZE)
RR3_1 = "fingerprint" + ZONE1 + " IN TXT " + str(fingerprint_size)

RR1_2 = "capacity" + ZONE2 + " IN TXT " + str(CAPACITY)
RR2_2 = "buckets" + ZONE2 + " IN TXT " + str(BUCKET_SIZE)
RR3_2 = "fingerprint" + ZONE2 + " IN TXT " + str(fingerprint_size)

# 1st: Create Cuckoo Filter zone with each RR corresponding to a single bucket
RR_1st = list()
RRs_2nd = list()
for index in range(0, CAPACITY):
    RR = str(index) + ZONE1 + " IN TXT "
    RR_temp = str()
    for item in contents_hex[index]:
        RR_temp += item
    RR += RR_temp
    if RR_temp == "":
        RR += "."
    RR_1st.append(RR)
    if len(contents_hex[index]) < 4:
        RRs_2nd.append(RR_temp + ".")
    else:
        RRs_2nd.append(RR_temp)

file_1st = open("/root/dnspriv/bandwidth_experiments/cuckooFilterZoneFiles/bindReadyFiles/file_1st", "w")
file_1st.write(RR1_1 + "\n")
file_1st.write(RR2_1 + "\n")
file_1st.write(RR3_1 + "\n")
for line in RR_1st:
    if line[-1] == ".":
        continue
    file_1st.write(line + "\n")

# 2nd: Create Cuckoo Filter zone with each RR corresponding to multiple buckets
current_RR = str()
current_RR_size = 0
current_RR_sequence = 0
RRs_2nd_configured = list()
for item in RRs_2nd:
    if current_RR_size + len(item) <= 255:
        current_RR += item
        current_RR_size += len(item)
    else:
        remaining = 255 - current_RR_size
        total = remaining + current_RR_size
        current_RR += item[0:remaining]
        RR = str(current_RR_sequence) + ZONE2 + " IN TXT " + current_RR
        RRs_2nd_configured.append(RR)
        current_RR = str()
        current_RR = item[remaining:]
        current_RR_size = len(item[remaining:])
        current_RR_sequence += 1

RR = str(current_RR_sequence) + ZONE2 + " IN TXT " + current_RR
RRs_2nd_configured.append(RR)

file_2nd = open("/root/dnspriv/bandwidth_experiments/cuckooFilterZoneFiles/bindReadyFiles/file_2nd", "w")
file_2nd.write(RR1_2 + "\n")
file_2nd.write(RR2_2 + "\n")
file_2nd.write(RR3_2 + "\n")
for line in RRs_2nd_configured:
    file_2nd.write(line + "\n")
