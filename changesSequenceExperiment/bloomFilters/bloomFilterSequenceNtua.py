import BloomFilter
import bitarray
import time
import dynamic_dns

# Constants 
zoneFileName = "/root/dnspriv/zone_files/ntua_names"
sizeOfFilter = 159760
hashFunctions = 3
ZONE = ".bf.example.com"


if __name__ == "__main__":
    initialBfCreationStartTime = time.time()
    # Create the Bloom Filter that will hold the names of the DNS zone
    bf = BloomFilter.createBloomFilter(sizeOfFilter, hashFunctions)
    # Fill in Bloom Filter with the names of the DNS zone
    bf = BloomFilter.fillBloomFilter(zoneFileName, bf)
    initialBfCreationEndTime = time.time()
    print("Created Initial Bloom Filter in: ", initialBfCreationEndTime - initialBfCreationStartTime)

    # Make the changes in the Bloom Filter from the journalfile. Bloom Filter is reconstructed.
    changesStartTime = time.time()
    bf = BloomFilter.createBloomFilter(sizeOfFilter, hashFunctions)
    bf = BloomFilter.fillBloomFilter(zoneFileName, bf)
    changesDict = dynamic_dns.getDynamicChanges()
    for key in changesDict:
        if changesDict[key].decode("utf-8") == "add":
            bf.add(key.decode("utf-8"))
    changesEndTime = time.time()
    print("Changes incorporated for Bloom Filter in: ", changesEndTime - changesStartTime)

    # Create the Bloom Filter Zone File
    zoneFileCreationStartTime = time.time()
    # Export the Bloom Filter as a string of bits
    bfBitarrayString = bf.exportBloomFilter().to01()
    # Split the bitarray into chucks of one byte, but still represented in bits
    bitChunks = [bfBitarrayString[i : (i + 8)] for i in range(0, sizeOfFilter, 8)]
    # Convert each chuck to a Byte in Hex representation
    byteChunks = [int(bitString, base=2) for bitString in bitChunks]
    hexRepresentation = [format(item, 'x') for item in byteChunks]
    # If the number has one digit, insert 0 in front of the number
    finalRepresentation = list()
    for hexNumber in hexRepresentation:
        itemToInsert = hexNumber
        if int(hexNumber, 16) <= 15:
            itemToInsert = "0" + itemToInsert
        finalRepresentation.append(itemToInsert)
    # Join all lists together
    completeList = ''.join(finalRepresentation)
    # Form the lines to add in the zone file
    lines = [completeList[i : (i + 128)] for i in range(0, int(2 * sizeOfFilter / 8), 128)]
    # Create the Bloom Filter Zone File
    bfZoneFile = open("./bfZoneFiles/ntuaBfZoneFile.txt", "w")
    sequence = 0
    for line in lines:
        lineToAdd = str(sequence) + ZONE + " IN TXT " + line
        bfZoneFile.write(lineToAdd + "\n")
        sequence += 1
    zoneFileCreationEndTime = time.time()
    print("Zone File Created in: ", zoneFileCreationEndTime - zoneFileCreationStartTime)
