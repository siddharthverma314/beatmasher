class Beat:
    '''A beat is a list of tracks. Each beat also contains a resolution,
    which is the amount of time each 0 or 1 is held for, ex. 32nd
    note, 16th note, etc. This is stored as an integer containing the
    number 32 or 16 respectively.
    Right now, the program assumes a 4/4 rhythm so the resolution must
    be in powers of 2.
    '''

    def __init__(self, name="", resolution=8):
        self.tracks = [] 
        self.resolution = resolution
        self.name = name

class Track:
    '''Each track can be represented by a list of 1s and 0s, where a 1 is a
    note played on a midi number, and 0 is a note rest. It also
    contains a uniqueness value, which the user assigns based on the
    uniqueness of the sound of the note. '''

    def __init__(self, midiNumber, beatList=[], uniqueness=0):
        self.midiNumber = midiNumber
        self.beatList = beatList
        self.uniqueness = uniqueness
        self.noteUniqueness = []

    def __getitem__(self, index):
        if isinstance(index, int):
            length = len(self.beatList)
            return self.beatList[index % length]
