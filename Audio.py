def getAudio(path, filename):
    from scipy.io import wavfile
    import librosa # For situations where SciPy cannot open wav file (error about incomplete chunk...)
    import math
    import numpy as np

    if path[-1] != "/":
        path += "/"

    if type(filename) != tuple:
        try:
            fs, data = wavfile.read(path + filename)
        except Exception as e:
            data, fs = librosa.load(path + filename, sr=None)
    else:
        first = True
        for aFile in filename:
            if first == True:
                try:
                    fs, data = wavfile.read(path + aFile)
                except Exception as e:
                    data, fs = librosa.load(path + aFile, sr=None)
                first = False
            else:
                try:
                    fFs, fData = wavfile.read(path + aFile)
                except Exception as e:
                    fData, fFs = librosa.load(path + aFile, sr=None)
                if fFs != fs:
                    print("The audio files need to have the same sampling frequency.")
                    # Note this does not throw an error, should make it do so
                data = np.concatenate((data, fData), axis=1)

    mins = math.floor(len(data)/(fs * 60))
    secs = round((len(data)/(fs) - 60 * mins)*100)/100

    try:
        nChannels = data.shape[1]
    except IndexError:
        nChannels = 1

    if nChannels == 1:
        print("The audio file was sampled at {:,} Hz with {:,} samples overall and {} channel.".format(fs, len(data), nChannels))
    else:
        print("The audio file was sampled at {:,} Hz with {:,} samples overall and {} channels.".format(fs, len(data), nChannels))
    print("The length of the file is {} mins {:3} secs.".format(mins, secs))
    
    return(fs, data)
