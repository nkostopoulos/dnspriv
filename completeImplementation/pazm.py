import math
import struct
from cuckoo.filter import CuckooFilter
import bitarray
import os
import time
from time import sleep
import dynamic_dns
import subprocess
import sys

########################################
####### WARNING: Based on BIND 9 #######
########################################



# The zone file to parse
ZONE_FILE = "ntua_names"
# The name of the Hashed DNS Zone
HASHED_DNS_ZONE = ".hz.tld."
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
    bucketSize = 4
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
    fqdnFreq = dict()
    for item in zone:
        item = item.rstrip()
        fqdn = item.split("\t")[0].split(" ")[0]
        fqdns.add(fqdn.lower())
        try:
            fqdnFreq[fqdn] += 1
        except:
            fqdnFreq[fqdn] = 1
    numberOfFqdns = len(fqdns)
    print("Number of Distinct FQDNs in ntua zone: ", numberOfFqdns)
    return fqdns, numberOfFqdns, fqdnFreq

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
    
    # 2nd: Create Cuckoo Filter zone with each RR corresponding to multiple buckets
    current_RR = str()
    current_RR_size = 0
    current_RR_sequence = 0
    RRs_configured = list()
    for item in RRs:
        if current_RR_size + len(item) <= 255:
            current_RR += item
            current_RR_size += len(item)
        else:
            remaining = 255 - current_RR_size
            total = remaining + current_RR_size
            current_RR += item[0:remaining]
            RR = str(current_RR_sequence) + HASHED_DNS_ZONE + " IN TXT " + current_RR
            RRs_configured.append(RR)
            current_RR = str()
            current_RR = item[remaining:]
            current_RR_size = len(item[remaining:])
            current_RR_sequence += 1

    RR = str(current_RR_sequence) + HASHED_DNS_ZONE + " IN TXT " + current_RR
    RRs_configured.append(RR)
    
    # Created the zone file
    hz = open("hashedDNSZone", "w")
    hz.write(RR1 + "\n")
    hz.write(RR2 + "\n")
    hz.write(RR3 + "\n")
    hz.write(RR4 + "\n")
    hz.write(RR5 + "\n")
    for line in RRs_configured:
        hz.write(line + "\n")

    # Load the zone. The hz.tld_temp file contains initial records, e.g. SOA, NS, etc.
    os.system("head /etc/bind/hz.tld > hz.tld_temp")
    os.system("cat hz.tld_temp hashedDNSZone > /etc/bind/hz.tld")
    os.system("rndc reload hz.tld")

def incorporateChanges(cuckoo, changesList, numberOfFqdns, fqdnFreq):
    '''
        Incorporate the changes received from the Zone Updates Log in the Cuckoo Filter
    '''
    # Why these frequency values? ----> RRs with different values or RR types may share the same FQDN
    doTheseChanges = list()
    for name_and_action in changesList:
        name = name_and_action[0]
        action = name_and_action[1]
        if action == "del":
            fqdnFreq[name] -= 1
            if fqdnFreq[name] == 0:
                cuckoo.delete(name)
                numberOfFqdns -= 1
                doTheseChanges.append(name_and_action)
        if action == "add":
            try:
                fqdnFreq[name] += 1
            except:
                fqdnFreq[name] = 1
            if fqdnFreq[name] == 1:
                cuckoo.insert(name)
                numberOfFqdns += 1
                doTheseChanges.append(name_and_action)
                # will drop an exception if the size item is inserted more that 2 * bucketSize times
                # this is included in the code of the Cuckoo Filter implementation
    return cuckoo, numberOfFqdns, fqdnFreq, doTheseChanges

def formIzRRs(cuckoo, doTheseChanges, RR_index):
    '''
        Form the Resource Records that will be added in the Incremental DNS Zones
    '''
    RRs_inc = list()
    for name_and_action in doTheseChanges:
        name = name_and_action[0]
        action = name_and_action[1]
        fp, indices = cuckoo.get_fingerprint(name)
        first = indices[0]
        second = indices[1]
        RR = "update add " + str(RR_index) + ".iz.tld 86400 IN TXT \"" + action + " " + str(fp) + " " + str(first) + "," + str(second) + "\""
        RRs_inc.append(RR)
        RR_index += 1
    return cuckoo, RR_index, RRs_inc

def updateIz(RRs_inc):
    ''' 
        Update the Incremental DNS Zone with the Resource Records
    '''
    fd = open("inc_update.txt", "w")
    fd.write("server spiderman.netmode.ece.ntua.gr\n")
    fd.write("zone iz.tld\n")
    for RR in RRs_inc:
        fd.write(RR + "\n")
    fd.write("show\n")
    fd.write("send\n")
    return None

def findSerialNumber():
    '''
        Find the serial number of the Incremental DNS Zone
    '''
    proc = subprocess.Popen("dig SOA @spiderman.netmode.ece.ntua.gr iz.tld | grep SOA", stdout = subprocess.PIPE, shell = True)
    (out, err) = proc.communicate()
    last_serial = out.split(b"\t")[-1].split(b" ")[2].decode("utf-8")
    return last_serial

def updateLastSerial(lastSerial):
    '''
        Update the Incremental DNS Zone with the last serial that was incorporated in the Hashed DNS Zones
    '''
    fd = open("inc_update.txt", "w")
    fd.write("server spiderman.netmode.ece.ntua.gr\n")
    fd.write("zone iz.tld\n")
    fd.write("update del last-serial.iz.tld\n")
    fd.write("update add last-serial.iz.tld 86400 IN TXT " + str(lastSerial) + "\n")
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
    fqdns, numberOfFqdns, fqdnFreq = getFqdns()
    
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

    serial = findSerialNumber()
    
    # We do not want to renew the Hashed DNS Zone when there were no changes
    hadChanges = "No"

    while 1:
        sleep(60)
        if (time.time() - izUpdated > INCREMENTAL_DNS_ZONE_UPDATE):
            changesList = dynamic_dns.getDynamicChanges()
            if changesList != None:
                cuckoo, numberOfFqdns, fqdnFreq, doTheseChanges = incorporateChanges(cuckoo, changesList, numberOfFqdns, fqdnFreq)
                if doTheseChanges != []:
                    hadChanges = "Yes"
                    cuckoo, RR_index, RRs_inc = formIzRRs(cuckoo, doTheseChanges, RR_index)
                    updateIz(RRs_inc)
                    os.system("nsupdate -k keys.conf -v inc_update.txt")
    
        if (time.time() - hzCreated > HASHED_DNS_ZONE_RENEWAL):
            last_serial = findSerialNumber()
            if hadChanges == "Yes":
                updateLastSerial(last_serial)
                os.system("nsupdate -k keys.conf -v inc_update.txt")
                createHashedZone(cuckoo, contentsHex, buckets, bucketSize, fingerprintSize)
                current_serial = last_serial
                hadChanges = "No"
            hzCreated = time.time()
