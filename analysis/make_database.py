import midi, os
import constructs.database as database
import constructs.beat as beat

DEFAULT_RESOLUTION = 64 #smallest duration that can be stored

def loadDatabase(pathToDatabase="../database", resolution=DEFAULT_RESOLUTION):
    '''This function creates a database out of all midi files in a folder. The 
    folder must contain only midi files or this function will not work.
    '''
    #load files
    db = database.Database()
    files = {}
    names = os.listdir(pathToDatabase)
    for name in names:
        files[name] = midi.read_midifile("../database/" + name)
        loadFile(files[name], db, resolution, files, name)
    return db

def loadFile(midiFile, d, resolution, files, name):
    '''Loads one midi file into a database d.
    @param d: The database to input the midi file into.
    @param midiFile: The midi object of the file.
    @param resolution: The smallest duration of a note, ex 32 = 1/32th note
    '''
    resolution /= 8
    myBeat = beat.Beat()
    myBeat.name = name
    index = 0
    for event in midiFile[0]:
        if event.tick != 0:
            index += int(float(event.tick) / midiFile.resolution * resolution)
        addBeat(event, myBeat, index)
    d.beats.append(myBeat)
    #fill with zeros
    maxLen = 256 #HARD-CODED
    for i in xrange(len(myBeat.tracks)):
        myBeat.tracks[i].beatList += [0]*(maxLen-len(myBeat.tracks[i].beatList))

def addBeat(event, myBeat, index):
    midiNumbers = [track.midiNumber for track in myBeat.tracks]
    try:
        i = midiNumbers.index(event.get_pitch())
        for j in xrange(index - len(myBeat.tracks[i].beatList)):
            myBeat.tracks[i].beatList.append(0)
        if isinstance(event, midi.NoteOffEvent):
            return
        myBeat.tracks[i].beatList.append(1)
    except ValueError:
        myBeat.tracks.append(beat.Track(event.get_pitch(), [0]*index+ [1]))
    except AttributeError:
        pass
    
