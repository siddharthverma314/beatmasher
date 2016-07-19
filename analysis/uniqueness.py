import math, pickle

#constant weights
WEIGHT_USER = 2
WEIGHT_DISSIMILARITY = 1
WEIGHT_PERIODICITY = 1
WEIGHT_LENGTH = 1

WEIGHT_NEGATIVE = -1
WEIGHT_POSITIVE = 1

WEIGHT_PREVIOUS_DATABASE = 1
WEIGHT_USER_DATABASE = 1

def uniquenessOfBeat(beat, database=None):
    '''Analyses a given beat and returns a value of uniqueness of each
    track as a dictionary.'''

    '''Rules of weighing beats
    1. Periodicity - if the time period is longer, the beat gets a
    higher score.
    2. Dissimilarity from database - The less a track is similar with
    any other track in the database, the higher a score it gets.
    3. Uniqueness given by user.
    4. Number of notes in track.
    
    Each feature is assigned a value from 0 to 1, and this is weighted
    and averaged to get a final value of uniqueness. The return value
    ranges from 0 to 1.'''

    midiList = [track.midiNumber for track in beat.tracks]

    #User-provided uniqueness
    userUniqueness = [track.uniqueness for track in beat.tracks]
    userUniqueness = normalize(userUniqueness)
    userUniqueness = [i * WEIGHT_USER for i in userUniqueness]

    #Periodicity
    periodicity = []
    for i in xrange(len(beat.tracks)):
        periodicity.append(getPeriodicity(beat.tracks[i].beatList))
    periodicity = [math.log(i, 2) for i in periodicity]
    periodicity = normalize(periodicity)
    periodicity = [i * WEIGHT_PERIODICITY for i in periodicity]

    #Dissimilarity from database
    if(database != None):
        dissimilarity = []
        for i in xrange(len(beat.tracks)):
            dissimilarity.append(dissimilarityFromDatabase(database, beat.tracks[i].beatList))
        dissimilarity = normalize(dissimilarity)
        dissimilarity = [i * WEIGHT_DISSIMILARITY for i in dissimilarity]
    else:
        dissimilarity = 0

    #Number of notes
    length = []
    for i in xrange(len(beat.tracks)):
        pattern = beat.tracks[i].beatList
        count = 0
        for i in pattern:
            if i == 1:
                count += 1
        length.append(count)
    length = normalize(length)
    length = [(1-i) for i in length]
    length = [i * WEIGHT_LENGTH for i in length]

    #calculate average for uniqueness
    uniqueness = [u+p+d+l for u,p,d,l in zip(userUniqueness, periodicity,
                                             dissimilarity, length)]
    uniqueness = normalizeRange(uniqueness)

    #make uniqueness into a dictionary
    returnUniqueness = {}
    for i in xrange(len(midiList)):
        returnUniqueness[midiList[i]] = uniqueness[i]
    return returnUniqueness
        
def getPeriodicity(beatList):
    '''To get the periodicitiy, a beatList is sliced into a number
    smaller than the length and repeated till the end of the
    list. The lists then undergo logical XOR then summed up'''

    periodicities = [] #list of periodicities for integral lengths
    for i in xrange(1, len(beatList)):
        temp = 0 #sum of periodicities
        for j in xrange(len(beatList)):
            match = xnor(beatList[j], beatList[j%i])
            temp += WEIGHT_NEGATIVE if match == 0 else WEIGHT_POSITIVE
        periodicities.append(temp)
    index = periodicities.index(max(periodicities)) + 1
    return index if index < len(beatList)/2 else len(beatList)
    
def normalize(someList):
    '''This function converts all values in a list to be in a range of
    0 to 1. It assumes that the list contains only numeric values.'''

    #find maximum of list
    maxList = max(someList)

    #divide all numbers by maxList
    if maxList != 0:
        return [float(i)/maxList for i in someList]
    else:
        return someList

def normalizeRange(someList):
    minimum = min(someList)
    maximum = max(someList)
    someList = [i-minimum for i in someList]
    return [float(i)/maximum for i in someList]

def dissimilarityFromDatabase(database, track):
    '''Finds the dissimilarity of a track from a given database.'''
    dissimilarity = 0
    for dbeat in database.beats:
        tempBeat = 0
        for dtrack in dbeat.tracks:
            #calculate dissimilarity index
            temp = 0
            for i in xrange(len(track)):
                temp += xor(dtrack.beatList[i], track)
            temp /= float(dbeat.resolution)
            tempBeat += temp
        tempBeat /= float(len(dbeat.tracks))
        dissimilarity += tempBeat
    dissimilarity /= float(len(database.beats))
    return dissimilarity

def xnor(a, b):
    return 1 if a == b else 0

def xor(a, b):
    return 1 if a != b else 0

def xnorSumList(lista, listb):
    '''xnors and sums a list'''
    #assuming that the lists are of the same length
    sum = 0
    for i in xrange(lista):
        sum += xnor(lista[i], listb[i])

def uniquenessOfNotes(inputTrack, database=None):
    '''Check against precompiled and user database to determine which
    notes are more unique or less played than others.

    '''

    #get weights from compiled database
    weights_database = pickle.load(open('../analysis/weights.data', 'rb'))
    weights_database = [i*WEIGHT_PREVIOUS_DATABASE for i in weights_database]

    weights_user = [0]*len(database.beats[0].tracks[0].beatList)
    if database != None:
        for beat in database.beats:
            for track in beat.tracks:
                for i in xrange(len(track.beatList)):
                    weights_user[i] += track.beatList[i]
    weights_user = normalize(weights_user)
    weights_user = [1-i for i in weights_user]
    weights_user = [i*WEIGHT_USER_DATABASE for i in weights_user]

    #make final list by removing values with 0
    final_weights = [(i+j) for i, j in zip(weights_user, weights_database)]
    final_weights = normalize(final_weights)
    uniqueness = []
    for i in xrange(len(final_weights)):
        if inputTrack.beatList[i] == 1:
            uniqueness.append(final_weights[i])
        else:
            uniqueness.append(0)
    
    return uniqueness

def processDatabase(database):
    for beat in database.beats:
        processBeat(beat, database)

def processBeat(beat, db):
    #insert uniqueness into beat
    u = uniquenessOfBeat(beat, db)
    uSorted = sorted(u.values())
    for track in beat.tracks:
        track.uniqueness = \
        float(uSorted.index(u[track.midiNumber]))/len(uSorted)
        track.noteUniqueness = uniquenessOfNotes(track, db)
        #print track.uniqueness
