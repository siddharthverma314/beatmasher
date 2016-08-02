import pickle, math, random
import constructs.beat as beat
import patterns

def sample(someList):
    '''Returns an index from a list using values as probabilities'''
    #generate incremental list
    count = 0
    probabilities = [0]
    for i in someList:
        count += i
        probabilities.append(count)
    #normalize probabilities
    maximum = float(max(probabilities))
    if(maximum != 0):
        probabilities = [float(i)/maximum for i in probabilities]
    del maximum
    #generate random number and choose value that fits
    r = random.random()
    for i in xrange(len(probabilities) - 1):
        if probabilities[i] < r <= probabilities[i+1]:
            return i
    else:
        return None

class Create:
    '''This method returns a track with a midi number and a uniqueness
    @param uniqueness The uniqueness of the track to be made
    @param midiNumber The midiNumber of the track to be made
    @param length The length of the track to be made (in resolution)'''
    def createTrack(self, uniqueness, midiNumber):
        raise NotImplementedError

class CreateRandom(Create):

    def __init__(self):
        self.weights = pickle.load(open('../analysis/weights.data', 'rb'))
        self.weights = [float(i/max(self.weights)) for i in self.weights]
        self.OFFSET = 2
        
    def createTrack(self, uniqueness, midiNumber, number=None, length=256):
        '''Returns a track with specified uniqueness with "number" number of
        notes'''

        #set Numberfunction if None
        if number is None:
            number = self.numberFunction(uniqueness)

        #generate list of indices
        weights = [math.pow(i, (uniqueness+self.OFFSET)*2) for i in self.weights] #fuzzy AND
        indices = []
        for i in xrange(number):
            index = sample(self.weights)
            if index in indices:
                continue
            if indices == range(len(self.weights)):
                break
            indices.append(index)

        #create Track
        track = beat.Track(midiNumber)
        track.uniqueness = uniqueness
        track.beatList = self.createBeatList(indices, length)
        return track

    def numberFunction(self, uniqueness):
        '''Defines how many notes should be played for a given uniqueness value'''
        return int((-29 * uniqueness + 30) ** 1.0/1.5)

    def createBeatList(self, indices, maxLen):
        '''Creates a list with 0s and 1s where the positions of the 1s are the
        elements of the list '''
        beatList = [0] * maxLen
        for i in indices:
            beatList[i] = 1
        return beatList
        

class CreatePattern(Create):
    '''This class creates a track from patterns, which is a Markov model.'''

    def __init__(self):
        self.stm = patterns.loadPatterns()

    def createTrack(self, uniqueness, midiNumber, length=31):
        #generate STM and starting point
        pattern = self.selectStart(uniqueness, self.stm)
        beatList = pattern.beatList
        #fill in beatList
        for i in xrange(length):
            pattern = self.selectNext(pattern, self.stm)
            beatList += pattern.beatList
        #package track
        track = beat.Track(midiNumber)
        track.uniqueness = uniqueness
        track.beatList = beatList
        return track

    def selectStart(self, uniqueness, stm):
        #generate list of uniqueness
        choices = [i.uniqueness for i in stm.keys()]
        #generate list of probabilities
        choices = [i - uniqueness for i in choices]
        choices = [i - min(choices) for i in choices]
        #select one starting point
        choice = sample(choices)
        #return the that track
        return stm.keys()[choice]

    def selectNext(self, pattern, stm):
        #select the key from the STM
        choices = [i.beatList for i in stm.keys()]
        index = choices.index(pattern.beatList)
        choice = stm.keys()[index]
        #select one choice from a key
        return random.choice(stm[choice])
