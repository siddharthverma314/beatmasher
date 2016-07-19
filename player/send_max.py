import time
import analysis.make_database as make_database
import analysis.uniqueness as uniqueness
import constructs.database as database
import player.OSC as OSC

#variables
PORT_SEND = 15928
PORT_RECV = 8082

#setup variabes
count = 0
beatToPlay = None

#variables
offset = 0
db = make_database.loadDatabase()
uniqueness.processDatabase(db)

#methods
def normalize(alist):
    rlist = []
    mlist = max(alist)
    if mlist == 0:
        mlist = 1
    for i in alist:
        rlist.append(float(i)/mlist)
    return rlist

def playBeat(beat):
    global beatToPlay
    beatToPlay = beat
    server.serve_forever()
    server.close()

def playBang(addr, tags, msg, client_address):
    global count, offset

    #index of track and note to insert
    convertedTrack = convertListToIndices([t.uniqueness for t in beatToPlay.tracks])
    trackIndex, rem = clipNumber(offset ,max(convertedTrack))
    trackIndex2 = convertedTrack.index(trackIndex)

    convertedNote = beatToPlay.tracks[trackIndex2].noteUniqueness
    convertedNote = convertListToIndices(convertedNote)
    convertedNote = normalize(convertedNote)
    newBeatList = [0 if i <= rem else 1 for i in convertedNote]

    #exchange newBeatList and beatList
    beatList = beatToPlay.tracks[trackIndex2].beatList
    beatToPlay.tracks[trackIndex2].beatList = newBeatList
    
    message = OSC.OSCMessage('/midi')
    for i in xrange(len(beatToPlay.tracks)):
        note = beatToPlay.tracks[i].beatList[count]
        if note == 1 and convertedTrack[i] >= trackIndex:
            message.append(beatToPlay.tracks[i].midiNumber)
    client.send(message)
    
    beatToPlay.tracks[trackIndex2].beatList = beatList
    count += 1
    count %= 256

def clipNumber(value, num):
    '''Converts a value between 0 and 1 to an integer between 0 and
    num. Returns a tuple of the number and the
    remainder'''
    flooredValue = int(value * num)
    remainder = value * num - flooredValue
    return flooredValue, remainder

def convertListToIndices(alist):
    '''Returns a list of the indices of the sorted list, and removes 0s'''
    #sort list
    sortedList = sorted(alist)
    #remove zeros
    number = 0
    for i in xrange(0, len(sortedList)):
        if sortedList[i] == 0:
            number += 1
    for i in xrange(number - 1):
        sortedList.remove(0)
    #add indices to finalList and set them to zero in code
    finalList = []
    for i in xrange(len(alist)):
        index = sortedList.index(alist[i])
        finalList.append(index)
        sortedList[index] = 0
    return finalList

def setOffset(addr, tags, msg, client_address):
    global offset
    offset = float(msg[0])/127

#setup OSC objects
client = OSC.OSCClient()
server = OSC.OSCServer(('localhost', PORT_RECV))

client.connect(('localhost', PORT_SEND))
server.addDefaultHandlers()
server.addMsgHandler('/tempo', playBang)
server.addMsgHandler('/uniqueness', setOffset)
try:
    playBeat(db.beats[2])
except KeyboardInterrupt:
    server.close()

