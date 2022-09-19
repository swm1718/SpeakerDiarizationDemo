def saveSCPFile(path, meeting, frameSegments):
    if path[-1] != "/":
        path += "/"
    txt = ""
    for row in frameSegments:
        txt += "{}_{}_{}={}.fea[{},{}]\n".format(meeting, row[0], row[1], meeting, row[0], row[1])
    with open(path + meeting + ".scp", "w") as f:
        f.write(txt)

def saveRTTMFile(path, audioname, timeSegments):
    if path[-1] != "/":
        path += "/"
    txt = ""
    for row in timeSegments:
        txt += "SPEAKER {} 1 {:09.3f} {:06.3f} <NA> <NA> {} <NA>\n".format(audioname, row[0], round(row[1] - row[0], 3), row[3])
    with open(path + audioname + ".rttm", "w") as f:
        f.write(txt)
