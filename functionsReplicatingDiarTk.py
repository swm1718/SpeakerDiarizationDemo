# This file sets out the Python functions that replicate aspects of DiarTk

def getXSegs(combinedSegs):
    """
    
    
    """
    import math
    xSegs = []
    for row in combinedSegs:
        rowLen = row[1] - row[0]
        if rowLen > 250:
            n = math.floor(rowLen/250)
            r = rowLen%250
            for i in range(n):
                xSegs.append([int(row[0]+250*i), int(row[0]+250*i+249)])
            # For short last xSeg need to include last frame
            if r != 0:
                xSegs.append([int(row[0]+250*n), int(row[0]+ 250*n+r)])
        else:
            xSegs.append(row)
    nXSegs = len(xSegs)
        
    return nXSegs, xSegs


def getFeatures(nXSegs, xSegs):
    """
    
    """
    import math
    nFrames = 0
    for i in range(nXSegs):
        nFramesSeg = xSegs[i][1] - xSegs[i][0] + 1
        xSegs[i].append(nFramesSeg)
        nFrames += nFramesSeg

    for i in range(nXSegs):
        wts = xSegs[i][2]/nFrames
        xSegs[i].append(wts)
        logwts = math.log(wts)
        xSegs[i].append(logwts)
        
    return nFrames, xSegs


def getXMeans(mfccs, xSegs):
    """
    
    """
    import numpy as np

    nMfccs = len(mfccs[0])

    xMeans = []
    for row in xSegs:
        xMfccs = [[] for i in range(nMfccs)]

        # No frame shifts applied - I used -1 in the Excel spreadsheet, but on reflection I am not sure that is right as 
        # time 0 is frame 0 and time 0.01 is frame 1, so no need to adjust start frame.
        # End frame needs shift as time goes to end of frame.
        # Update - I have now subtracted 1 from both to try to match the DiarTk figures
        for frame in range(row[0]-1, row[1]):
            for i in range(nMfccs):
                xMfccs[i].append(mfccs[frame][i])

        xMeans.append([np.mean(m) for m in xMfccs])
        
    return nMfccs, xMeans


def getMeansVars(nMfccs, mfccs, xSegs):
    """
    
    """
    import numpy as np
    meanVec = [0 for i in range(nMfccs)]
    varsVec = [0 for i in range(nMfccs)]
    nFrames = 0
    for row in xSegs:
        segStart = row[0] - 1
        segEnd = row[1] - 1
        #print("{}, {}".format(segStart, segEnd))
        nFrames += segEnd - segStart + 1
        for frame in range(segStart, segEnd + 1):
            meanVec = np.add(meanVec, mfccs[frame])
            varsVec = np.add(varsVec, mfccs[frame]**2)
    print(nFrames)
    meanVec = [m/nFrames for m in meanVec]
    varsVec = [m/nFrames for m in varsVec]
    
    return meanVec, varsVec


def getAllVars(nMfccs, meanVec, varsVec):
    """
    
    """
    #MIN_POS_FLOAT = 1.4e-45 # Not sure this does anything in practice, is from DiarTk
    #allVars = [max((varsVec[i] - max(meanVec[i], MIN_POS_FLOAT)**2)/25, 0.000001) for i in range(nMfccs)]
    # The smoothing value of 25 is hardwired into DiarTk, and is changed to 60 if TDOA features are used
    # The minimum value of 10e-6 = 1e-5 = 0.00001 is also hardwired into DiarTk, and distinct from VAR_TH
    allVars = [max((varsVec[i] - meanVec[i]**2)/25, 0.00001) for i in range(nMfccs)]
    return allVars


def getRevisedMeans(nMfccs, xMeans, allVars):
    """
    
    """
    import numpy as np
    revisedMeans = []
    for x in range(len(xMeans)):
        revisedMeans.append([xMeans[x][i]/allVars[i] for i in range(nMfccs)])

    revisedMeans = np.array(revisedMeans)

    return revisedMeans


def getL2_x(nMfccs, nXSegs, xMeans, allVars):
    """
    
    """
    l2_x = [0 for x in range(nXSegs)]

    for x in range(nXSegs):
        for i in range(nMfccs):
            l2_x[x] += xMeans[x][i]**2/allVars[i]

    return l2_x


def getDfXSegs(nXSegs, xSegs, l2_x):
    import pandas as pd

    for x in range(nXSegs):
        xSegs[x].append(l2_x[x])
        xSegs[x].append(xSegs[x][-2] - 0.5*xSegs[x][-1])

    columns = ["Start Frame", "End Frame", "Number of Segments", "wts", "logwts", "l2_x", "new logwts"]
    dfXSegs = pd.DataFrame(xSegs, columns=columns)
    
    return dfXSegs


def getPosteriors(nXSegs, xSegs, mfccs, revisedMeans):
    import time
    import numpy as np
    import math

    startTime = time.time()
    t = time.localtime()
    print("Cell started at {:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec))

    posteriors = np.zeros((len(mfccs), nXSegs))
    maxLklds = []
    posteriors2 = np.zeros((len(mfccs), nXSegs))

    for x in range(nXSegs):
        print("xSegment: {}".format(x), end="\r")
        # Note I have not subtracted 1 from these frames, unlike the ones above
        # This is what DiarTk does, though I am not comfortable with it
        startFrame = xSegs[x][0]
        endFrame = xSegs[x][1]
        # Extract mfccs relevant for this x segment
        xMfccs = mfccs[startFrame: endFrame+1]
        
        # Iterate over segments
        for y in range(len(xMfccs)):
            
            # Need to iterate over x segments again as there are 348 outputs per frame
            for z in range(nXSegs):
                tempTerm = xSegs[z][6] # Start with new logwts of x segment
                tempTerm += np.sum(np.multiply(xMfccs[y], revisedMeans[z])) # Use dot product then sum
                
                #for m in range(nMfccs):
                #    tempTerm += mfccs[startFrame+y, m] * revisedMeans[z][m]

                posteriors[startFrame+y, z] = tempTerm
                
            # When all tempTerms calculated for a frame, find max likelihood and sum of likelihoods for that frame then
            # calculate normalized posteriors as exp(tempTerm - maxLkld)/sumLkld
            maxLkld = max(posteriors[startFrame+y])
            maxLklds.append(maxLkld)
            #print(maxLkld)
            for z in range(nXSegs):
                p = math.exp(posteriors[startFrame+y, z] - maxLkld)
                if p >= 1.4e-45:
                    posteriors2[startFrame+y, z] = p
                else:
                    posteriors2[startFrame+y, z] = 0

            sumLkld = sum(posteriors2[startFrame+y])
            for z in range(nXSegs):
                if posteriors2[startFrame+y, z] > 0:
                    posteriors2[startFrame+y, z] /= sumLkld
                
    endTime = time.time()

    print("This cell took {:.2f} seconds to run.".format(endTime-startTime))

    return posteriors, maxLklds, posteriors2


def getFeats(nXSegs, xSegs, posteriors):
    """

    """
    import numpy as np

    feats = np.zeros((nXSegs, nXSegs))

    for x in range(nXSegs):
        startFrame = xSegs[x][0]
        endFrame = xSegs[x][1]
        posts = posteriors[startFrame: endFrame+1]
        feats[x] = (np.round(np.sum(posts, axis=0))).astype(int)

    return feats


def klDivergence(vX, vY):
    """
    
    """
    import math
    # vX and vY are probability vectors p(...)
    # No checks about suitable probability vectors inserted
    sum = 0
    for i in range(len(vX)):
        # This is the commented out if statement in DiarTk, for some reason it only has
        # the first part now
        if vX[i] > 0 and vY[i] > 0:
            sum += vX[i] * math.log(vX[i]/vY[i])
    return sum


def jsDivergence(v1, v2, p1, p2):
    """
    
    """
    # Not sure about these two rows, it just seems that DiarTk does this
    #v1 = v1/250
    #v2 = v2/250

    vAve = v1*p1 + v2*p2
    #print("vAve is length {}".format(vAve.shape))
    #print("vAve is {}".format(vAve))
    return p1*klDivergence(v1, vAve) + p2*klDivergence(v2, vAve)


def entropy(p1, p2):
    """
    
    """
    import math
    return -(p1*math.log(p1) + p2*math.log(p2))


def calcDeltaF(v1, v2, p1, p2, beta):
    """
    
    """
    term1 = (p1+p2) * jsDivergence(v1, v2, p1/(p1+p2), p2/(p1+p2))
    term2 = (p1+p2) * entropy(p1/(p1+p2), p2/(p1+p2))
    return term1 - (1/beta)*term2


def calcDeltaFParallel(a):
    """
    
    """
    v1 = a[0]
    v2 = a[1]
    p1 = a[2]
    p2 = a[3]
    beta = a[4]
    count = a[5]

    term1 = (p1+p2) * jsDivergence(v1, v2, p1/(p1+p2), p2/(p1+p2))
    term2 = (p1+p2) * entropy(p1/(p1+p2), p2/(p1+p2))
    if count < 2:
        print("deltaFs[{}] is {:.6f}".format(count, term1-(1/beta)*term2))
        print("term1 is {:.6f} and term2 is {:.6f}".format(term1, term2))
        print("v1 is {}".format(v1))
        print("p1 is {}".format(p1))
        print("v2 is {}".format(v2))
        print("p2 is {}".format(p2))
        print()
    return term1 - (1/beta)*term2


def getLstIter(newFeats):
    """
    
    """
    lstIter = []
    for i in range(len(newFeats)):
        if newFeats[i][0] != "N/A":
            lstIter.append(i)
    return lstIter


def getBestMerge(newFeats, xSegs, lstP, beta):
    """
    
    """
    import numpy as np
    # Iterate over each row up to penultimate row, exclude last one
    lstIter = getLstIter(newFeats)
    for i in range(len(lstIter)-1):
        # Iterate over all possible rows after the row starting from, which can include last one
        for j in range(i+1, len(lstIter)):
            #deltaF = calcDeltaF(np.array(newFeats[lstIter[i]]), np.array(newFeats[lstIter[j]]), xSegs[lstIter[i]][3], xSegs[lstIter[j]][3], beta)
            deltaF = calcDeltaF(np.array(newFeats[lstIter[i]]), np.array(newFeats[lstIter[j]]), \
                    lstP[lstIter[i]], lstP[lstIter[j]], beta)
            # Set first deltaF as lowest to start with
            if i == 0 and j == 1:
                minDelta = deltaF
                minI = lstIter[0]
                minJ = lstIter[1]
            elif deltaF < minDelta:
                minDelta = deltaF
                minI = lstIter[i]
                minJ = lstIter[j]

    return minI, minJ


def getBestMergeParallel(newFeats, xSegs, lstP, beta):
    """
    This function identifies the clusters that minimise the reduction in the deltaF values (i.e. the reduction in the objective function).

    Inputs:

    Outputs:
    
    """
    import math
    import numpy as np
    import multiprocessing as mp
    from multiprocessing import Pool

    #deltaFs = np.ones((len(lstIter)-1, len(lstIter-1))) # Assumes the minimum deltaF values always less than 1
    deltaFs = []
    lstIter = getLstIter(newFeats)

    pts = []
    for i in range(len(lstIter)-1):
        for j in range(i+1, len(lstIter)):
            pts.append([i, j])

    with Pool(mp.cpu_count()) as p:
        deltaFs.append(p.map(calcDeltaFParallel,\
            [[np.array(newFeats[lstIter[pt[0]]]), np.array(newFeats[lstIter[pt[1]]]), lstP[lstIter[pt[0]]], lstP[lstIter[pt[1]]], beta, index]\
            for index, pt in enumerate(pts)]))

    # Convert to a row vector before finding location of minimum
    minDeltaFPosition = np.argmin(deltaFs)
    minI = lstIter[pts[minDeltaFPosition][0]]
    minJ = lstIter[pts[minDeltaFPosition][1]]

    return minI, minJ


def mergeClusters(nXSegs, newFeats, clusters, lstP, c1, c2, lstMerges):
    """
    
    """
    import numpy as np
    p1 = lstP[c1]
    p2 = lstP[c2]
    #print("p1 is {} and p2 is {}".format(p1, p2))
    newFeats[c1] = list(np.add((p1/(p1+p2)) * np.array(newFeats[c1]), (p2/(p1+p2)) * np.array(newFeats[c2])))
    newFeats[c2] = ["N/A" for i in range(nXSegs)]
    
    lstMerges.append([c1, c2])
    # Replace all relevant clusters with new cluster (e.g. if 315 -> 163 then 163 -> 115)
    for i in range(len(clusters)):
        if clusters[i] == c2:
            clusters[i] = c1
    
    # Similarly need to replace my cluster probabilities with the new ones
    lstP[c1] = lstP[c1] + lstP[c2]
    lstP[c2] = "N/A"
    
    return newFeats, clusters, lstP, lstMerges


def countClusters(newFeats):
    """
    
    """
    count = 0
    for row in newFeats:
        if row[0] != "N/A":
            count += 1
    return count


def getClusters(nXSegs, newFeats, clusters, lstP, lstMerges, beta, parallel):
    import time
    import math

    startTime = time.time()
    t = time.localtime()
    print("Cell started at {:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec))

    maxClust = 10
    while countClusters(newFeats) > maxClust:
        print("Number of clusters: {}  ".format(countClusters(newFeats)), end="\r")
        if parallel:
            c1, c2 = getBestMergeParallel(newFeats, nXSegs, lstP, beta)
        else:
            c1, c2 = getBestMerge(newFeats, nXSegs, lstP, beta)
        newFeats, clusters, lstP, lstMerges = mergeClusters(nXSegs, newFeats, clusters, lstP, c1, c2, lstMerges)
        
    endTime = time.time()
    totalTime = endTime - startTime
    hrs = math.floor(totalTime/3600)
    mins = math.floor((totalTime - hrs*3600)/60)
    secs = totalTime - hrs*3600 - mins*60

    print("This cell took {} hrs, {} mins, {:.2f} secs to run.".format(hrs, mins, secs))

    return newFeats, clusters, lstP, lstMerges


def numberClusters(clusters):
    """

    """
    renumberedClusters = []
    dictClusters = {}
    
    # To reduce clustered speaker xSegs to numbers 0 to maxclust-1
    count = 0
    for num in clusters:
        if num not in dictClusters:
            dictClusters[num] = count
            count += 1            
        
    for num in clusters:
        renumberedClusters.append(dictClusters[num])
        
    return renumberedClusters, dictClusters


