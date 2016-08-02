'''This module will create a bunch of patterns and store it as a state
transition matrix. Patterns are small chunks of beats that can be
combined together to create different tracks. A pattern can look
something like this:

[1, 0, 0, 0, 1, 0, 0, 1]

Each pattern is one measure long, and stores its uniqueness. When
composing a new beat, the first pattern is selected based on a
uniqueness value given to the program, and then uses a markov chain to
complete the pattern.'''

import analysis.make_database as make_database
import analysis.uniqueness as uniqueness

PATTERNS_FILE="patterns.data" #file in which markov patterns will be stored

class Pattern:
    def __init__(self):
        self.beatList = []
        self.uniqueness = 0

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(tuple([tuple(self.beatList), self.uniqueness]))

def makePatterns(databasePath="../database/"):
    stateTransitionMatrix = {}
    db = make_database.loadDatabase()
    uniqueness.processDatabase(db)
    for beat in db.beats:
        for track in beat.tracks:
           listOfPatterns = _stringPatterns(track)
           _addToStateTransitionMatrix(listOfPatterns, stateTransitionMatrix)
    return stateTransitionMatrix

def loadPatterns(patternsPath=PATTERNS_FILE):
    return makePatterns()

def _stringPatterns(track, resolution=8):
    patterns = []
    for i in xrange(0, len(track.beatList), resolution):
        #split beatList
        beatList = track.beatList[i:i+resolution]

        #create pattern out of splitted beatList
        pattern = Pattern()
        pattern.beatList = beatList
        pattern.uniqueness = track.uniqueness
        patterns.append(pattern)
    return patterns

def _addToStateTransitionMatrix(listOfPatterns, stm):
    for i in xrange(len(listOfPatterns) - 1):
        if listOfPatterns[i] not in stm.keys():
            stm[listOfPatterns[i]] = [listOfPatterns[i+1]]
        else:
            stm[listOfPatterns[i]].append(listOfPatterns[i+1])

if __name__ == "__main__":
    makePatterns()
