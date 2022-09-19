def writeHtkFile(features, nSampPeriod, filename, nParmKind):
    import struct

    nSamples = len(features)
    nSampPeriod = nSampPeriod
    nSampSize = len(features[0]) * 4 # I think the 4 represents the number of bytes needed for floats
    nParmKind = nParmKind # 6 for MFCCs

    # This uses big endian > to represent the header in 12 bytes
    header = struct.pack('>iihh', nSamples, nSampPeriod, nSampSize, nParmKind)

    # Need to flatten MFCCs into 1D array before packing
    packedData = struct.pack('>%sf' % features.size, *features.flatten('c'))

    with open(filename, "wb") as f:
        f.write(header + packedData)
        print("The file size is {:,} kB.".format(round(len(header + packedData)/1024)))
