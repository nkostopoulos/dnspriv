import BloomFilter
import bitarray
import time
import dynamic_dns
import textwrap

# Constants 
zoneFileName = "ru.zone"
zoneFileName2 = "ru.zone2"
sizeOfFilter = 102574158
hashFunctions = 3
ZONE = ".bf.example.com"


if __name__ == "__main__":
    initialBfCreationStartTime = time.time()
    zone = open(zoneFileName, "r")
    fqdns = set()
    for item in zone:
        item = item.rstrip()
        fqdn = item.split("\t")[0].split(" ")[0]
        fqdns.add(fqdn.lower())

    # Create the Bloom Filter that will hold the names of the DNS zone
    bf = BloomFilter.createBloomFilter(sizeOfFilter, hashFunctions)
    # Fill in Bloom Filter with the names of the DNS zone
    bf = BloomFilter.fillBloomFilterSet(fqdns, bf)
    initialBfCreationEndTime = time.time()
    print("Created Initial Bloom Filter in: ", initialBfCreationEndTime - initialBfCreationStartTime)

    # Make the changes in the Bloom Filter from the journalfile. Bloom Filter is reconstructed.
    changesStartTime = time.time()
    zone = open(zoneFileName, "r")
    fqdns = set()
    for item in zone:
        item = item.rstrip()
        fqdn = item.split("\t")[0].split(" ")[0]
        fqdns.add(fqdn.lower())
    changesList = dynamic_dns.getDynamicChanges()
    for item in changesList:
        name = item[0] + "."
        action = item[1]
        if action == "del":
            fqdns.remove(name)
    bf2 = BloomFilter.createBloomFilter(sizeOfFilter, hashFunctions)
    bf2 = BloomFilter.fillBloomFilterSet(fqdns, bf2)
    for item in changesList:
        name = item[0]
        action = item[1]
        if action == "add":
            bf2.add(name)
    changesEndTime = time.time()
    print("Changes incorporated for Bloom Filter in: ", changesEndTime - changesStartTime)
