import midi, os
import constructs.database as database
import constructs.beat as beat

DEFAULT_RESOLUTION = 64

def loadDatabase(pathToDatabase="../database", resolution=DEFAULT_RESOLUTION):
    #load files
    db = database.Database()
    files = {}
    names = os.listdir(pathToDatabase)
    for name in names:
        files[name] = midi.read_midifile("../database/" + name)
        loadFile(name, db, resolution, files)
    return db

def loadFile(name, d, resolution, files):
    resolution /= 8
    myBeat = beat.Beat()
    myBeat.name = name
    index = 0
    for event in files[name][0]:
        if event.tick != 0:
            index += int(float(event.tick) / files[name].resolution * resolution)
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
    
