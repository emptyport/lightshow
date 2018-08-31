"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import numpy as np

file = open("melbands.txt", "r")
melbands = file.readlines()
melbands_start_times = []
melbands_vals = []

for line in melbands:
    melbands_start_times.append(float(line.rstrip().split()[0]))

    rawVals = line.rstrip().split()[1:]
    arr = []
    for val in rawVals:
        arr.append(float(val))
    melbands_vals.append(np.asarray(arr))

TIME_DIFF = 0.041667

val_boxed = [melbands_vals[0]]
time_boxed = [melbands_start_times[0]]
val_queue = []
time_queue = []
for i in range(1, len(melbands_vals)):
    val_queue.append(melbands_vals[i])
    time_queue.append(melbands_start_times[i])
    if melbands_start_times[i] - time_boxed[-1] > TIME_DIFF:
        val_boxed.append(np.mean(val_queue, axis=0))
        time_boxed.append((time_queue[-1] + time_queue[0])/2)
        val_queue = []
        time_queue = []

nVals = np.size(val_boxed[0])
nMap = 10

x = np.linspace(0, 1, nVals)
newX = np.linspace(0, 1, nMap)

mapped_val_boxed = []
for y in val_boxed:
    newY = np.interp(newX, x, y)
    mapped_val_boxed.append(newY)

for i in range(0, len(mapped_val_boxed)):
    lowerBound = i
    if lowerBound < 0:
        lowerBound = 0
    upperBound = i+40
    if upperBound > len(mapped_val_boxed):
        upperBound = len(mapped_val_boxed)
    maxVals = np.max(mapped_val_boxed[lowerBound:upperBound], axis=0)
    newVals = 255*mapped_val_boxed[i]/maxVals
    newVals = newVals.astype(int)
    mapped_val_boxed[i] = newVals

outfile = open('boxed_melbands.txt', 'w')
for i in range(0, len(val_boxed)):
    outfile.write(str(time_boxed[i]))
    outfile.write('\t')
    outfile.write(str(val_boxed[i]))
    outfile.write('\n')
outfile.close()

file = open("pitch.txt", "r")
pitch = file.readlines()
pitch_vals = []
pitch_start_times = []
for line in pitch:
    pitch_vals.append(float(line.rstrip().split()[1]))
    pitch_start_times.append(float(line.rstrip().split()[0]))

file = open("beats.txt", "r") 
beats = file.readlines() 

file = open("onsets.txt", "r") 
onsets = file.readlines()

file = open("notes.txt", "r") 
notes = file.readlines()
note_vals = []
start_times = []
for line in notes:
    if len(line.rstrip().split()) > 1:
        note_vals.append(float(line.rstrip().split()[0]))
        start_times.append(float(line.rstrip().split()[1]))
    
if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
start_time = time.time()
next_beat = float(beats.pop(0))
next_onset = float(onsets.pop(0))
next_note_val = note_vals.pop(0)
next_note_start = start_times.pop(0)
next_pitch_val = pitch_vals.pop(0)
next_pitch_start = pitch_start_times.pop(0)
next_melbands_val = mapped_val_boxed.pop(0)
next_melbands_start = time_boxed.pop(0)
while stream.is_active():
    if time.time() - start_time >= next_beat:
        #print "Beat",str(next_beat)
        next_beat = float(beats.pop(0))

    if time.time() - start_time >= next_onset:
        print "Onset",str(next_onset)
        next_onset = float(onsets.pop(0))

    if time.time() - start_time >= next_note_start:
        #print next_note_val,"Note",next_note_start
        next_note_val = note_vals.pop(0)
        next_note_start = start_times.pop(0)
    
    if time.time() - start_time >= next_pitch_start:
        #print "Pitch",next_pitch_val
        next_pitch_val = pitch_vals.pop(0)
        next_pitch_start = pitch_start_times.pop(0)

    if time.time() - start_time >= next_melbands_start:
        print ' '.join(['%3.f']*len(next_melbands_val)) % tuple(next_melbands_val)
        #print next_melbands_val
        next_melbands_val = mapped_val_boxed.pop(0)
        next_melbands_start = time_boxed.pop(0)

    time.sleep(0.000001)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio (7)
p.terminate()