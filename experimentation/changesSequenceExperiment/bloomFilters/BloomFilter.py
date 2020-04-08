from bitarray import bitarray
import mmh3
import sys
from math import log, ceil, exp

class BloomFilter:
    def __init__(self, size, hashCount):
        self.size = size # the size of the bloom filter in bits
        self.hashCount = hashCount # the number of hash functions the filter uses
        self.bitArray = bitarray(size) # the bloom filter itself
        self.bitArray.setall(0) # initialize bloom filter with zeroes

    def exportBloomFilter(self):
        return self.bitArray

    def add(self, string):
        for seed in range(self.hashCount):
            result = mmh3.hash(string, seed) % self.size
            self.bitArray[result] = 1
        return None

    def query(self, string):
        for seed in range(self.hashCount):
            result = mmh3.hash(string, seed) % self.size
            if self.bitArray[result] == 0:
                return False
        return True

def createBloomFilter(filterSize, hashFunctions):
    if filterSize == 0 or hashFunctions == 0:
        print("Invalid Arguments. Exiting...")
        sys.exit(1)
    else:
        bf = BloomFilter(filterSize, hashFunctions)
    return bf

def fillBloomFilterSet(mySet, bloomFilter):
    for item in mySet:
        bloomFilter.add(item)

    return bloomFilter

def fillBloomFilter(fileName, bloomFilter):
    fileToOpen = open(fileName,"r")
    for line in fileToOpen:
        nameToAdd = line.rstrip() 
        bloomFilter.add(nameToAdd)

    return bloomFilter
