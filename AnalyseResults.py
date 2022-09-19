def getDERs(path, clusters=False):
    import pandas as pd

    flag = False
    if clusters == False:
        filenames = ["NISTEvaluation_2_5.txt", "NISTEvaluation_2_0.txt", "NISTEvaluation_1_5.txt"]
        filenames += ["NISTEvaluation_1_0.txt", "NISTEvaluation_0_5.txt", "NISTEvaluation_0_0.txt"]
    else:
        filenames = ["NISTEvaluation_clusters_2_5.txt", "NISTEvaluation_clusters_2_0.txt", "NISTEvaluation_clusters_1_5.txt"]
        filenames += ["NISTEvaluation_clusters_1_0.txt", "NISTEvaluation_clusters_0_5.txt", "NISTEvaluation_clusters_0_0.txt"]
    results = []
    if path[-1] != "/":
        path += "/"

    for file in filenames:
        with open(path + file, "r") as f:
            for line in f:
                if line.find("Performance analysis for Speaker Diarization for ALL") != -1:
                    flag = True
                if flag == True:
                    #print(line)
                    if line.find("SCORED SPEAKER TIME") != -1:
                        lineItems = line.split()
                        scoredTime = float(lineItems[4])
                    elif line.find("MISSED SPEAKER TIME") != -1:
                        lineItems = line.split()
                        missedTime = float(lineItems[4])
                    elif line.find("FALARM SPEAKER TIME") != -1:
                        lineItems = line.split()
                        falarmTime = float(lineItems[4])
                    elif line.find("SPEAKER ERROR TIME") != -1:
                        lineItems = line.split()
                        errorTime = float(lineItems[4])
                    elif line.find("OVERALL SPEAKER DIARIZATION ERROR") != -1:
                        lineItems = line.split(" ")
                        DER = float(lineItems[6])
                        results.append
                        collar = file[-7] + file[-5]
                        collar = (int(collar) * 10) # Expressing in ms
                        results.append([collar, round(missedTime/scoredTime, 4)*100, round(falarmTime/scoredTime, 4)*100, round(errorTime/scoredTime, 4)*100, DER])
            flag = False

    df = pd.DataFrame(results, columns=["Collar (ms)", "MISSED (%)", "FALARM (%)", "ERROR (%)", "DER (%)"])
    return df

def getMappings(path):
    import os
    txt = ""
    for filename in os.listdir(path):
        if filename.find("NISTEvaluation") != -1:
            txt += path + filename + "\n"
            with open(path + filename, "r") as f:
                for line in f:
                    if line.find("=>") != -1 or line.find("matched") != -1:
                        txt += line
            txt += "\n"

    return txt

def getDERs2(path, clusters=False):
    import pandas as pd
    import re

    flag = False
    if clusters == False:
        filenames = ["NISTEvaluation_2_5_Perl.txt", "NISTEvaluation_2_0_Perl.txt", "NISTEvaluation_1_5_Perl.txt"]
        filenames += ["NISTEvaluation_1_0_Perl.txt", "NISTEvaluation_0_5_Perl.txt", "NISTEvaluation_0_0_Perl.txt"]
    else:
        filenames = ["NISTEvaluation_clusters_2_5.txt", "NISTEvaluation_clusters_2_0.txt", "NISTEvaluation_clusters_1_5.txt"]
        filenames += ["NISTEvaluation_clusters_1_0.txt", "NISTEvaluation_clusters_0_5.txt", "NISTEvaluation_clusters_0_0.txt"]
    results = []
    if path[-1] != "/":
        path += "/"

    for file in filenames:
        with open(path + file, "r") as f:
            lst = []
            for line in f:

                # Count number of diarized speakers
                if line.find("spkr_") != -1:
                    lnItems = re.split("\_ | \'", line)
                    lst.append(lnItems[-1])

                # Get DERs
                if line.find("Performance analysis for Speaker Diarization for ALL") != -1:
                    flag = True
                if flag == True:
                    #print(line)
                    if line.find("SCORED SPEAKER TIME") != -1:
                        lineItems = line.split()
                        scoredTime = float(lineItems[4])
                    elif line.find("MISSED SPEAKER TIME") != -1:
                        lineItems = line.split()
                        missedTime = float(lineItems[4])
                    elif line.find("FALARM SPEAKER TIME") != -1:
                        lineItems = line.split()
                        falarmTime = float(lineItems[4])
                    elif line.find("SPEAKER ERROR TIME") != -1:
                        lineItems = line.split()
                        errorTime = float(lineItems[4])
                    elif line.find("OVERALL SPEAKER DIARIZATION ERROR") != -1:
                        lineItems = line.split(" ")
                        DER = float(lineItems[6])
                        results.append
                        collar = file[-12] + file[-10]
                        collar = (int(collar) * 10) # Expressing in ms
                        results.append([collar, len(set(lst)), round(missedTime/scoredTime, 4)*100, round(falarmTime/scoredTime, 4)*100, round(errorTime/scoredTime, 4)*100, DER])
            flag = False

    df = pd.DataFrame([results[i] for i in range(int(len(results)-1), -1, -1)], \
                    columns=["Collar (ms)", "nDiarizedSpkrs", "MISSED (%)", "FALARM (%)", "ERROR (%)", "DER (%)"])
    return df