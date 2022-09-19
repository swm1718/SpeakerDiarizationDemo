# This file returns both the time segments for RTTM format and segments for SCP format
def AMIXMLtoSegs(path, meeting, fp):
    import os
    import math

    timeSegments = []
    frameSegments = []

    if path[-1] != "/":
        path += "/"

    for filename in os.listdir(path):
        # print(filename)
        if filename.find(meeting) != -1 and filename.find("segments.xml") != -1:
            with open(path + filename, "r") as f:
                for line in f:
                    if line.find("transcriber_start") != -1:
                        lineItems = line.replace(" ", "").split("\"")
                        #print(lineItems)
                        timeSegments.append([float(lineItems[5]), float(lineItems[7]), filename[8]])
    timeSegments.sort(key=lambda x: x[0])
    for row in timeSegments:
        # Note use of floor and ceil here, could alternatively just round
        frameSegments.append([math.floor(row[0] / fp), math.ceil(row[1] / fp), row[2]])

    with open(path + "meetings.xml") as f:
        spkrs = []
        for line in f:
            if line.find(meeting) != -1 and line.find("global_name") != -1:
                gn = line.find("global_name")
                spkrs.append([line[line.find("nxt_agent") + 11], line[gn + 13: gn + 19]])

    # In timeSegments, replace generic speaker description with more precise AMI description
    timeSegmentsNew = []
    for row in timeSegments:
        for row2 in spkrs:
            if row[2] == row2[0]:
                timeSegmentsNew.append(row + [row2[1]])

    return (timeSegmentsNew, frameSegments, spkrs)


# This file returns both the time segments for RTTM format and segments for SCP format
# This is the September 2020 update that better fits the AMI Corpus Manual structure
def AMIXMLtoSegs2(path1, path2, meeting, fp):
    """
    INSERT
    Inputs:
    - path1 is the path to the meetings.xml file
    - path2 is the path to the segments.xml files
    Outputs:
    - INSERT
    """
    import os
    import math

    timeSegments = []
    frameSegments = []

    if path1[-1] != "/":
        path1 += "/"
    if path2[-1] != "/":
        path2 += "/"

    for filename in os.listdir(path2):
        # print(filename)
        if filename.find(meeting) != -1 and filename.find("segments.xml") != -1:
            with open(path2 + filename, "r") as f:
                for line in f:
                    if line.find("transcriber_start") != -1:
                        lineItems = line.replace(" ", "").split("\"")
                        #print(lineItems)
                        timeSegments.append([float(lineItems[5]), float(lineItems[7]), filename[8]])
    timeSegments.sort(key=lambda x: x[0])
    for row in timeSegments:
        # Note use of floor and ceil here, could alternatively just round
        frameSegments.append([math.floor(row[0] / fp), math.ceil(row[1] / fp), row[2]])

    with open(path1 + "meetings.xml") as f:
        spkrs = []
        for line in f:
            if line.find(meeting) != -1 and line.find("global_name") != -1:
                gn = line.find("global_name")
                spkrs.append([line[line.find("nxt_agent") + 11], line[gn + 13: gn + 19]])

    # In timeSegments, replace generic speaker description with more precise AMI description
    timeSegmentsNew = []
    for row in timeSegments:
        for row2 in spkrs:
            if row[2] == row2[0]:
                timeSegmentsNew.append(row + [row2[1]])

    return timeSegmentsNew, frameSegments, spkrs
