import math
import struct
from cuckoo.filter import CuckooFilter
import bitarray
import time

CAPACITY = 4000
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
    cuckoo.insert(fqdn)

chars1 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
chars2 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']
chars3 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']
chars4 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']
chars5 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']
chars6 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']

matches = set()
total_words = 0
total_matches = 0
start_time = time.time()
for item1 in chars1:
    for item2 in chars2:
        for item3 in chars3:
            for item4 in chars4:
                for item5 in chars5:
                    for item6 in chars6:
                        word = item1 + item2 + item3 + item4 + item5 + item6
                        total_words += 1
                        if cuckoo.contains(word) == True:
                            total_matches += 1
                            matches.add(word)
end_time = time.time()

print("False Positive Ratio: ", total_matches / total_words * 100)
print("Total Matches including False Positives: ", total_matches)
print("Total Matches including False Positives counterd by the set: ", len(matches))
print("Total Words Checked: ", total_words)

true_positives = set()
for item in matches:
    item = item.split(".")[0]
    if item in fqdns:
        true_positives.add(item)

print("True Positives: ", len(true_positives))
print("Time elapsed: ", end_time - start_time)
