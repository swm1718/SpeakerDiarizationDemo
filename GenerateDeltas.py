# calcuate over 2n + 1 = 9 points, so n = 4
def calcDeltas(matrix):
    ''' This function takes an input features matrix (e.g. MFCCs) in np.array format and calculates deltas from +/- 4 points '''
    import numpy as np
    import sys
    
    nRows = len(matrix)
    nCols = len(matrix[0])
    deltas = np.zeros((nRows, nCols))
    
    mFirst = matrix[0, :].reshape(1, nCols)
    mLast = matrix[-1, :].reshape(1, nCols)
    for i in range(nRows):
        if i >= 4 and i <= nRows - (4 + 1):
            x = matrix[i - 4: i + 5, :]
        elif i == 3:
            x = np.concatenate((mFirst, matrix[i - 3: i + 5, :]), axis=0)
        elif i == 2:
            x = np.concatenate((mFirst, mFirst, matrix[i - 2: i + 5, :]), axis=0)
        elif i == 1:
            x = np.concatenate((mFirst, mFirst, mFirst, matrix[i - 1: i + 5, :]), axis=0)
        elif i == 0:
            x = np.concatenate((mFirst, mFirst, mFirst, mFirst, matrix[i: i + 5, :]), axis=0)
        elif i == nRows - 4:
            x = np.concatenate((matrix[i - 4: i + 4, :], mLast), axis=0)
        elif i == nRows - 3:
            x = np.concatenate((matrix[i - 4: i + 3, :], mLast, mLast), axis=0)
        elif i == nRows - 2:
            x = np.concatenate((matrix[i - 4: i + 2, :], mLast, mLast, mLast), axis=0)
        elif i == nRows - 1:
            x = np.concatenate((matrix[i - 4: i + 1, :], mLast, mLast, mLast, mLast), axis=0)

        for j in range(nCols):
            deltas[i, j] = (-4*x[0, j] - 3*x[1, j] - 2*x[2, j] - x[3, j] + x[5, j] + 2*x[6, j] + 3*x[7, j] + 4*x[8, j])/60

    return deltas

# calcuate over 2n + 1 = 9 points, so n = 4
def calcDeltaDeltas(matrix):
    ''' This function takes an input deltas matrix in np.array format and calculates deltas from +/- 1 point '''
    import numpy as np
    import sys
    
    nRows = len(matrix)
    nCols = len(matrix[0])
    deltaDeltas = np.zeros((nRows, nCols))
    
    for i in range(nRows):
        if i >= 1 and i <= nRows - (1 + 1):
            x = matrix[i - 1: i + 2, :]
            for j in range(nCols):
                deltaDeltas[i, j] = (-x[0, j] + x[2, j])/2
        elif i == 0:
            x = matrix[i: i + 2, :]
            for j in range(nCols):
                deltaDeltas[i, j] = (-x[0, j] + x[1, j])
        elif i == nRows - 1:
            x = matrix[i - 1: i + 1, :]
            for j in range(nCols):
                deltaDeltas[i, j] = (-x[0, j] + x[1, j])

    return deltaDeltas
