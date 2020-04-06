import BloomFilter
import bitarray

# Constants 
zoneFileName = "/root/dnspriv/zone_files/ru.zone"
sizeOfFilter = 102574158
hashFunctions = 3
ZONE = ".bf.example.com"


if __name__ == "__main__":
    # Create the Bloom Filter that will hold the names of the DNS zone
    bf = BloomFilter.createBloomFilter(sizeOfFilter, hashFunctions)
    # Fill in Bloom Filter with the names of the DNS zone
    bf = BloomFilter.fillBloomFilter(zoneFileName, bf)
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
    bfZoneFile = open("./bfZoneFiles/ruBfZoneFile.txt", "w")
    sequence = 0
    for line in lines:
        lineToAdd = str(sequence) + ZONE + " IN TXT " + line
        bfZoneFile.write(lineToAdd + "\n")
        sequence += 1
