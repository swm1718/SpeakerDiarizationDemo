def getStartTime(line):
    x0 = line.find("starttime=") + 11
    x1 = line.find("endtime=") - 2
    return float(line[x0:x1])

def getEndTime(line):
    x0 = line.find("endtime=") + 9
    if line.find("punc=") == -1 and line.find("trunc=") == -1 and line.find("mispronounced=") == -1 and line.find("pron=") == -1:
        x1 = line.find('">')
    elif line.find("punc=") != -1:
        x1 = line.find("punc=") - 2
    elif line.find("trunc=") != -1:
        x1 = line.find("trunc=") - 2
    elif line.find("mispronounced=") != -1:
        x1 = line.find("mispronounced=") - 2
    elif line.find("pron=") != -1:
        x1 = line.find("pron=") - 2
    else:
        print(error)
    return float(line[x0:x1])

def getWord(line):
    x0 = line.find('">') + 2
    x1 = line.find('</')
    return line[x0:x1]

def setSpeakerColour(speaker):
    if speaker == "A":
        speakerColour = "red"
    elif speaker == "B":
        speakerColour = "green"
    elif speaker == "C":
        speakerColour = "blue"
    elif speaker == "D":
        speakerColour = "yellow"
    else:
        speakerColour = "grey"
    return(speakerColour)

