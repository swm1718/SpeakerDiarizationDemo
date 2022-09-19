def getSegs(filename):
    segs = []
    with open(filename, "r") as f:
        for line in f:
            xStart = line.find("[")
            xEnd = line.find("]")
            lineItems = line[xStart + 1:xEnd].split(",")
            segs.append([int(lineItems[0]), int(lineItems[1])])
    return segs

def getSegsTime(rttmFilename):
    timeSegments = []
    with open(rttmFilename, "r") as f:
        for line in f:
            lineItems = line.split(" ")
            timeSegments.append([float(lineItems[3]), round(float(lineItems[3]) + float(lineItems[4]), 3)])
    return timeSegments

def getSegsTimeSpkr(rttmFilename):
    timeSegments = []
    with open(rttmFilename, "r") as f:
        for line in f:
            lineItems = line.split(" ")
            timeSegments.append([float(lineItems[3]), round(float(lineItems[3]) + float(lineItems[4]), 3), lineItems[7]])
    return timeSegments

def countOverlaps(array):
    count = 0
    for i in range(len(array) - 1):
        if array[i][1] > array[i+1][0]:
            count += 1
    return count

def findCombinedSegs(segs):
    combinedSegs = segs[:]
    overlapSpeechSegs = []

    while countOverlaps(combinedSegs) != 0:
        newCombinedSegs = []
        jump = False  # Flag to show when rows are being combined
        for i in range(len(combinedSegs) - 1):
            if jump == False:
                if combinedSegs[i][1] >= combinedSegs[i + 1][0]:
                    newCombinedSegs.append([combinedSegs[i][0], max(combinedSegs[i][1], combinedSegs[i + 1][1])])
                    overlapSpeechSegs.append([combinedSegs[i + 1][0], min(combinedSegs[i][1], combinedSegs[i + 1][1])])
                    jump = True
                else:
                    newCombinedSegs.append(combinedSegs[i])
            else:
                jump = False  # Only comes into play following a jump to say don't jump the next one
        # Now deal with last row depending on whether jumped or not
        if jump == False:
            newCombinedSegs.append(combinedSegs[-1])
        else:
            jump == False

        #print("There are now {} overlapping segments.".format(countOverlaps(combinedSegs)))

        combinedSegs = newCombinedSegs[:]

    overlapSpeechSegs.sort(key=lambda x: x[0])  # Not necessary for combinedSegs as it was sorted to start with

    while countOverlaps(overlapSpeechSegs) != 0:
        newOverlapSpeechSegs = []
        jump = False  # Flag to show when rows are being combined
        for i in range(len(overlapSpeechSegs) - 1):
            if jump == False:
                if overlapSpeechSegs[i][1] > overlapSpeechSegs[i + 1][0]:
                    newOverlapSpeechSegs.append(
                        [overlapSpeechSegs[i][0], max(overlapSpeechSegs[i][1], overlapSpeechSegs[i + 1][1])])
                    jump = True
                else:
                    newOverlapSpeechSegs.append(overlapSpeechSegs[i])
            else:
                jump = False  # Only comes into play following a jump to say don't jump the next one
        # Now deal with last row depending on whether jumped or not
        if jump == False:
            newOverlapSpeechSegs.append(overlapSpeechSegs[-1])
        else:
            jump == False

        # .sort(key=lambda x:x[0])

        overlapSpeechSegs = newOverlapSpeechSegs[:]

    return combinedSegs, overlapSpeechSegs

def findSingleSpeakerSegs(combinedSegs, overlapSpeechSegs):
    singleSpeakerSegs = []
    for i in range(len(combinedSegs)):
        firstOverlap = False  # Flag to add rowC to singleSpeakerSegs if it does not overlap with any overlapSpeechSegs frames
        secondOverlap = False  # Flag to indicate a second (or further) multiple speaker in speech segment

        for j in range(len(overlapSpeechSegs)):
            if combinedSegs[i][0] < overlapSpeechSegs[j][0] and combinedSegs[i][1] == overlapSpeechSegs[j][1] and secondOverlap == False:  # If both == nothing added
                singleSpeakerSegs.append([combinedSegs[i][0], overlapSpeechSegs[j][0] - 1])  # No need to worry about residual part
                firstOverlap = True
            elif combinedSegs[i][0] < overlapSpeechSegs[j][0] and combinedSegs[i][1] >= overlapSpeechSegs[j][1] and secondOverlap == False:
                singleSpeakerSegs.append([combinedSegs[i][0], overlapSpeechSegs[j][0] - 1])
                firstOverlap = True
                # for loop below only looks for second or more segments covered
                for k in range(len(overlapSpeechSegs) - j - 1, 0, -1):
                    # while secondOverlap == False:
                    if combinedSegs[i][1] >= overlapSpeechSegs[j + k][1] and secondOverlap == False:
                        secondOverlap = True
                        m = k
                if secondOverlap == True:
                    for n in range(m):
                        singleSpeakerSegs.append([overlapSpeechSegs[j + n][1] + 1, overlapSpeechSegs[j + n + 1][0] - 1])
                    singleSpeakerSegs.append([overlapSpeechSegs[j + n + 1][1] + 1, combinedSegs[i][1]])  # Add last part
                elif secondOverlap == False and firstOverlap == True:
                    singleSpeakerSegs.append([overlapSpeechSegs[j][1] + 1, combinedSegs[i][1]])
        if firstOverlap == False:
            singleSpeakerSegs.append(combinedSegs[i])

    return singleSpeakerSegs

def countSegs(array):
    nSegs = 0
    for row in array:
        nSegs += row[1] - row[0] + 1 # From and including to and including
    return nSegs

def returnSingleSpeakerSegs(filename):
    segs = getSegs(filename)
    combinedSegs, overlapSpeechSegs = findCombinedSegs(segs)
    return findSingleSpeakerSegs(combinedSegs, overlapSpeechSegs)

def createSingleSpeakerScpfile(path, filename):
    txt = ""
    prefix = filename[:-4]
    newScpfilename = prefix + "_SingleSpeakerSegmentsOnly.scp"
    for row in returnSingleSpeakerSegs(path + filename)[0]:
        txt += "{}_{}_{}={}.fea[{},{}]\n".format(prefix, row[0], row[1], prefix, row[0], row[1])
    with open(path + newScpfilename, "w") as f:
        f.write(txt)

def createUemfile(path, filename):
    segs = getSegs(path + filename)
    overlapSpeechSegs = findCombinedSegs(segs)[1]
    txt = ""
    prefix = filename[:-4]
    uemfilename = prefix + ".uem"
    for row in overlapSpeechSegs:
        txt += "{} 1 {} {}\n".format(prefix, row[0], row[1])
    with open(path + uemfilename, "w") as f:
        f.write(txt)

# findSingleSpeakerSegs does not work with times, hence this new definition
def findSingleSpeakerTimes(combinedSegs, overlapSpeechSegs):
    singleSpeakerSegs = []
    for i in range(len(combinedSegs)):
        firstOverlap = False  # Flag to add rowC to singleSpeakerSegs if it does not overlap with any overlapSpeechSegs frames
        secondOverlap = False  # Flag to indicate a second (or further) multiple speaker in speech segment

        for j in range(len(overlapSpeechSegs)):
            if combinedSegs[i][0] < overlapSpeechSegs[j][0] and combinedSegs[i][1] == overlapSpeechSegs[j][1] and secondOverlap == False:  # If both == nothing added
                singleSpeakerSegs.append([combinedSegs[i][0], overlapSpeechSegs[j][0]])  # No need to worry about residual part
                firstOverlap = True
            elif combinedSegs[i][0] < overlapSpeechSegs[j][0] and combinedSegs[i][1] >= overlapSpeechSegs[j][1] and secondOverlap == False:
                singleSpeakerSegs.append([combinedSegs[i][0], overlapSpeechSegs[j][0]])
                firstOverlap = True
                # for loop below only looks for second or more segments covered
                for k in range(len(overlapSpeechSegs) - j - 1, 0, -1):
                    # while secondOverlap == False:
                    if combinedSegs[i][1] >= overlapSpeechSegs[j + k][1] and secondOverlap == False:
                        secondOverlap = True
                        m = k
                if secondOverlap == True:
                    for n in range(m):
                        singleSpeakerSegs.append([overlapSpeechSegs[j + n][1], overlapSpeechSegs[j + n + 1][0]])
                    singleSpeakerSegs.append([overlapSpeechSegs[j + n + 1][1], combinedSegs[i][1]])  # Add last part
                elif secondOverlap == False and firstOverlap == True:
                    singleSpeakerSegs.append([overlapSpeechSegs[j][1], combinedSegs[i][1]])
        if firstOverlap == False:
            singleSpeakerSegs.append(combinedSegs[i])

    return singleSpeakerSegs