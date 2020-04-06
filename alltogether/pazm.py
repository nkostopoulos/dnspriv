import math
import struct
from cuckoo.filter import CuckooFilter
import bitarray
import os
import time
from time import sleep
import dynamic_dns
import subprocess

# The zone file to parse
ZONE_FILE = "ntua_names"
# The name of the Hashed DNS Zone
HASHED_DNS_ZONE = ".cf.example.com."
# How often the Hashed DNS Zone is renewed with the changes that occured in the last interval
HASHED_DNS_ZONE_RENEWAL = 3
# How often the Incremental DNS Zone is updated
INCREMENTAL_DNS_ZONE_UPDATE = 1

def setCuckooFilterParameters():
    ''' 
        Set the parameters of the Cuckoo Filter
        errorRate: probability of a False Positive to occur
        buckets: the number of available buckets in the Cuckoo Filter
        bucketSize: the number of entries per bucket
        fingerprintSize: the size of each fingerprint
    '''
    errorRate = 0.003
    buckets = 2305
    bucketSize = 16
    fingerprintSize = int(math.ceil(math.log(1.0 / errorRate, 2) + math.log(2 * bucketSize, 2)))
    return errorRate, buckets, bucketSize, fingerprintSize

def printCuckooFilterParameters(errorRate, buckets, bucketSize, fingerprintSize):
    '''
        Print the parameters of the Cuckoo Filter
    '''
    print("Cuckoo Filter Error Rate: ", errorRate)
    print("Cuckoo Filter Buckets: ", buckets)
    print("Cuckoo Filter Bucket Size: ", bucketSize)
    print("Fingerprint Size: ", fingerprintSize)
    return None

def initializeCuckooFilter(buckets, errorRate, bucketSize):
    '''
        Initialize the Cuckoo Filter that will hold the fingerprints of the zone FQDNs
    '''
    cuckoo = CuckooFilter(capacity = buckets, error_rate = errorRate, bucket_size = bucketSize)
    return cuckoo

def getFqdns():
    '''
        Get the distinct FQDNs included in the zone file that is going to be parsed
    '''
    zone = open(ZONE_FILE, "r")
    fqdns = set()
    for item in zone:
        item = item.rstrip()
        fqdn = item.split("\t")[0].split(" ")[0]
        fqdns.add(fqdn.lower())
    numberOfFqdns = len(fqdns)
    print("Number of Distinct FQDNs in ntua zone: ", numberOfFqdns)
    return fqdns, numberOfFqdns

def printLoadFactor(numberOfFqdns, buckets, bucketSize):
    '''
        Print the Load Factor of the Cuckoo Filter
        This is the number of stored items divided by the number of all the available entries
    '''
    loadFactor = numberOfFqdns / (buckets * bucketSize)
    print(loadFactor)
    return None

def exportCuckooFilterContents(cuckoo):
    '''
        Export the fingerprints of the Cuckoo Filter and their respective bucket indices
    '''
    filterItemsNumber = 0
    cuckooContents = cuckoo.export()
    contentsHex = list()
    for bucket in cuckooContents:
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
            filterItemsNumber += 1
        contentsHex.append(alist)
    print("Number of items stored in the filter: ", filterItemsNumber)
    return contentsHex

def createHashedZone(cuckoo, contentsHex, buckets, bucketSize, fingerprintSize):
    '''
        This creates the Hashed DNS Zone
    '''
    # Populate zone with the metadata
    RR1 = "buckets" + HASHED_DNS_ZONE + " IN TXT " + str(buckets)
    RR2 = "entries" + HASHED_DNS_ZONE + " IN TXT " + str(bucketSize)
    RR3 = "fp-size" + HASHED_DNS_ZONE + " IN TXT " + str(fingerprintSize)
    RR4 = "fp-algo" + HASHED_DNS_ZONE + " IN TXT fp-algo"
    RR5 = "hash-algo" + HASHED_DNS_ZONE + " IN TXT hash-algo"
    
    # 1st: Create RRs based on each bucket of the Cuckoo Filter
    RRs = list()
    for index in range(0, buckets):
        RR = str(index) + HASHED_DNS_ZONE + " IN TXT "
        RR_temp = str()
        for item in contentsHex[index]:
            RR_temp += item
        RR += RR_temp
        if RR_temp == "":
            RR += "."
        if len(contentsHex[index]) < 4:
            RRs.append(RR_temp + ".")
        else:
            RRs.append(RR_temp)
    
    # Set the size of each fingerprints in the Hashed DNS Zone
    # e.g. 9-12 bits correspond to 3 Hexadecimal digits
    if fingerprintSize <= 4:
        fp_zone_file = 1
    elif fingerprintSize <= 8:
        fp_zone_file = 2
    elif fingerprintSize <= 12:
        fp_zone_file = 3
    else:
        fp_zone_file = 4
    
    STEP = int(256 / (fp_zone_file * bucketSize))
    # 2nd: Create Cuckoo Filter zone with each RR corresponding to multiple buckets
    current_RR = str()
    current_RR_size = 0
    current_RR_sequence = 0
    RRs_configured = list()
    for item in RRs:
        if current_RR_size < STEP:
            current_RR += item
            current_RR_size += 1
        else:
            RR = str(current_RR_sequence) + HASHED_DNS_ZONE + " IN TXT " + current_RR
            RRs_configured.append(RR)
            current_RR = str()
            current_RR_size = 0
            current_RR_sequence += 1
    
    # Created the zone file
    hz = open("hashedDNSZone", "w")
    hz.write(RR1 + "\n")
    hz.write(RR2 + "\n")
    hz.write(RR3 + "\n")
    hz.write(RR4 + "\n")
    hz.write(RR5 + "\n")
    for line in RRs_configured:
        hz.write(line + "\n")

    # Load the zone. The cf.example.com_temp file contains initial records, e.g. SOA, NS, etc.
    os.system("head /etc/bind/cf.example.com > cf.example.com_temp")
    os.system("cat cf.example.com_temp hashedDNSZone > /etc/bind/cf.example.com")
    os.system("rndc reload cf.example.com")

def incorporateChanges(cuckoo, changesDict, numberOfFqdns):
    '''
        Incorporate the changes received from the Zone Updates Log in the Cuckoo Filter
    '''
    for key in changesDict:
        if changesDict[key].decode("utf-8") == "del":
            cuckoo.delete(key.decode("utf-8"))
            numberOfFqdns -= 1
        if changesDict[key].decode("utf-8") == "add":
            cuckoo.insert(key.decode("utf-8"))
            numberOfFqdns += 1
            # will drop an exception if the size item is inserted more that 2 * bucketSize times
            # this is included in the code of the Cuckoo Filter implementation
    return cuckoo, numberOfFqdns

def formIzRRs(cuckoo, changesDict, RR_index):
    '''
        Form the Resource Records that will be added in the Incremental DNS Zones
    '''
    RRs_inc = list()
    for key in changesDict:
        name = key.decode("utf-8")
        action = changesDict[key].decode("utf-8")
        fp, indices = cuckoo.get_fingerprint(name)
        first = indices[0]
        second = indices[1]
        RR = "update add " + str(RR_index) + ".cfinc.example.com 86400 IN TXT \"" + action + " " + str(fp) + " " + str(first) + "," + str(second) + "\""
        RRs_inc.append(RR)
        RR_index += 1
    return cuckoo, RR_index, RRs_inc

def updateIz(RRs_inc):
    ''' 
        Update the Incremental DNS Zone with the Resource Records
    '''
    fd = open("inc_update.txt", "w")
    fd.write("server spiderman.netmode.ece.ntua.gr\n")
    fd.write("zone cfinc.example.com\n")
    for RR in RRs_inc:
        fd.write(RR + "\n")
    fd.write("show\n")
    fd.write("send\n")
    return None

def findSerialNumber():
    '''
        Find the serial number of the Incremental DNS Zone
    '''
    proc = subprocess.Popen("dig SOA @spiderman.netmode.ece.ntua.gr cfinc.example.com | grep SOA", stdout = subprocess.PIPE, shell = True)
    (out, err) = proc.communicate()
    last_serial = out.split(b"\t")[-1].split(b" ")[2].decode("utf-8")
    return last_serial

def updateLastSerial(lastSerial):
    '''
        Update the Incremental DNS Zone with the last serial that was incorporated in the Hashed DNS Zones
    '''
    fd = open("inc_update.txt", "w")
    fd.write("server spiderman.netmode.ece.ntua.gr\n")
    fd.write("zone cfinc.example.com\n")
    fd.write("update del last-serial.cfinc.example.com\n")
    fd.write("update add last-serial.cfinc.example.com 86400 IN TXT " + str(lastSerial) + "\n")
    fd.write("show\n")
    fd.write("send\n")
    return None

if __name__ == "__main__":
    # Cuckoo Filter Parameters
    errorRate, buckets, bucketSize, fingerprintSize = setCuckooFilterParameters()
    printCuckooFilterParameters(errorRate, buckets, bucketSize, fingerprintSize)
    
    # Initialize the Cuckoo Filter
    cuckoo = initializeCuckooFilter(buckets, errorRate, bucketSize)
    
    # The DNS zone to parse
    fqdns, numberOfFqdns = getFqdns()
    
    # Print the load factor of the Cuckoo Filter
    printLoadFactor(numberOfFqdns, buckets, bucketSize)
    
    # Load the FQDNs of the monitored zone in the Cuckoo Filter
    for fqdn in fqdns:
        cuckoo.insert(fqdn)
    
    contentsHex = exportCuckooFilterContents(cuckoo)
    
    createHashedZone(cuckoo, contentsHex, buckets, bucketSize, fingerprintSize)
    
    RR_index = 0
    
    hzCreated = time.time()
    izUpdated = time.time()
    
    while 1:
        sleep(1)
        if (time.time() - izUpdated > INCREMENTAL_DNS_ZONE_UPDATE):
            print("We will update the Incremental DNS Zone")
            changesDict = dynamic_dns.getDynamicChanges()
            if changesDict != None:
                cuckoo, numberOfFqdns = incorporateChanges(cuckoo, changesDict, numberOfFqdns)
                printLoadFactor(numberOfFqdns, buckets, bucketSize)
                cuckoo, RR_index, RRs_inc = formIzRRs(cuckoo, changesDict, RR_index)
                updateIz(RRs_inc)
                os.system("nsupdate -k keys.conf -v inc_update.txt")
    
        if (time.time() - hzCreated > HASHED_DNS_ZONE_RENEWAL):
            print("We will renew the Hashed DNS Zone")
            last_serial = findSerialNumber()
            updateLastSerial(last_serial)
            os.system("nsupdate -k keys.conf -v inc_update.txt")
            createHashedZone(cuckoo, contentsHex, buckets, bucketSize, fingerprintSize)
            hzCreated = time.time()
