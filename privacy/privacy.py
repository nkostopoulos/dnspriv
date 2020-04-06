import math
import struct
from cuckoo.filter import CuckooFilter
import bitarray
import time

CAPACITY = 2305
ERROR_RATE = 0.003
BUCKET_SIZE = 4

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

# Load the FQDNs of the monitored zone in the Cuckoo Filter
for fqdn in fqdns:
    fqdn += ".ntua.gr"
    cuckoo.insert(fqdn)

chars = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']

total_words = 0
total_matches = 0
start_time = time.time()
for item1 in chars:
    for item2 in chars:
        for item3 in chars:
            for item4 in chars:
                for item5 in chars:
                    for item6 in chars:
                        word = item1 + item2 + item3 + item4 + ".ntua.gr"
                        if '-' in word[0]:
                            continue
                        total_words += 1
                        if cuckoo.contains(word) == True:
                            total_matches += 1
end_time = time.time()

print(total_matches / total_words * 100)
print(total_matches)
print(total_words)

print("Time elapsed: ", end_time - start_time)
