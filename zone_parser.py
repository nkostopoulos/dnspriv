from probables import (CuckooFilter)

# The DNS zone to parse
zone = open("netmode.ece.ntua.gr_zone", "r")

# Get the FQDNs of the DNS zone
fqdns = set()
for item in zone:
    item = item.rstrip()
    fqdn = item.split("\t")[0].split(" ")[0]
    fqdns.add(fqdn)

# Count the number of distinct FQDNs
number_of_fqdns = len(fqdns)
print("Number of Distinct FQDNs: ", number_of_fqdns)

# Add contents of the zone in the Cuckoo Filter
cko = CuckooFilter(capacity=48, bucket_size=4, max_swaps=50, auto_expand=False, finger_size=1)
for item in fqdns:
    cko.add(item)

# Get the contents of the Cuckoo Filters. Buckets are separated.
cf_zone_contents = cko.getSeparateContents()
print("The contents of the Cuckoo Filter are: ")
print(cf_zone_contents)

# Find the load factor of the Cuckoo Filter that represents the DNS zone
load_factor = cko.load_factor()
print("Load Factor is: ", load_factor)
