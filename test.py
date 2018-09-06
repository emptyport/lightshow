"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import numpy as np
import serial
import random

ARDUINO = True

# Connect to the Arduino
if ARDUINO:
    ser = serial.Serial('/dev/ttyACM0', 115200)

# This is for sending the data to the Arduino. Each brightness value is
# separated by : and the whole thing is enclosed in <>
# Example: <128:012:255>
def makeSerialString(arr):
    s = "<"
    for val in arr:
        s += str(val).zfill(3)
        s += ":"
    s = s[:-1]
    s += ">"
    return s

if len(sys.argv) < 4:
    print("Plays a wave file.\n\nUsage: %s filename.wav melbands.txt onsets.txt" % sys.argv[0])
    sys.exit(-1)

melbandFilename = sys.argv[2]
onsetFilename = sys.argv[3]

# melbands is our main thing
file = open(melbandFilename, "r")
melbands = file.readlines()
melbands_start_times = []
melbands_vals = []

# Just reading in the file
for line in melbands:
    melbands_start_times.append(float(line.rstrip().split()[0]))

    rawVals = line.rstrip().split()[1:]
    arr = []
    for val in rawVals:
        arr.append(float(val))
    melbands_vals.append(np.asarray(arr))

# We don't need millisecond precision for all the changes
# so we are going to smooth things out to 24 fps
TIME_DIFF = 0.041667

# The below code bins the melbands into windows that match 24 fps
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

# Now we want to map the melbands to how many channels we have
nVals = np.size(val_boxed[0])
nMap = 10
index_mapping = np.linspace(0, nMap-1, nMap).astype(int)

# Write to Arduino to make sure the lights are off
initialVals = []
for i in range(0, nMap):
    initialVals.append(0)
if ARDUINO:
    ser.write(makeSerialString(initialVals))

# We create an arbitrary x axis for our melbands
x = np.linspace(0, 1, nVals)
newX = np.linspace(0, 1, nMap)

# Now we interpolate the melbands to our channels
mapped_val_boxed = []
for y in val_boxed:
    newY = np.interp(newX, x, y)
    mapped_val_boxed.append(newY)

# Here we normalize the signal from 0 to 255, but we also get tricky and do the
# the normalization only 40 'frames' ahead. This way our signal is adjusting the
# normalization to the upcoming volume of the music. This still gives us the ability
# to adjust the lights with crescendos/decrescendos, but it also makes sure one loud
# part of the song doesn't make all the rest of the song very dim. The lowerbound code
# is leftover from when I was trying to find the best way to do this moving normalization
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

file = open(onsetFilename, "r") 
onsets = file.readlines()

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

# As the stream is playing I am going through the onsets and melbands
# and updating the channels. The melbands give the brightness values
# and the onsets say when to update those values because otherwise
# there is a lot of up and down in the signal

# wait for stream to finish (5)
start_time = time.time()
next_onset = float(onsets.pop(0))
next_melbands_val = mapped_val_boxed.pop(0)
next_melbands_start = time_boxed.pop(0)
shouldChange = True
while stream.is_active():

    if time.time() - start_time >= next_onset:
        shouldChange = True
        try:
            next_onset = float(onsets.pop(0))
        except:
            dummy = 0

    if time.time() - start_time >= next_melbands_start:
        if shouldChange:
            mean_val = np.mean(next_melbands_val)
            prob_cutoff = 0.5 * mean_val / 255
            if prob_cutoff > random.random():
                np.random.shuffle(index_mapping)
                print 'Shuffling'
            print ' '.join(['%3.f']*len(next_melbands_val)) % tuple(next_melbands_val)
            if ARDUINO:
                ser.write(makeSerialString(next_melbands_val[index_mapping].tolist()))
                ser.flushInput()
                ser.flushOutput()
            shouldChange = False
        try:
            next_melbands_val = mapped_val_boxed.pop(0)
            next_melbands_start = time_boxed.pop(0)
        except:
            dummy = 0

    time.sleep(0.01)

while np.mean(next_melbands_val) > 0:
    if next_melbands_val[i] > 0:
        next_melbands_val[i] = next_melbands_val[i] - 1
    print ' '.join(['%3.f']*len(next_melbands_val)) % tuple(next_melbands_val)
    if ARDUINO:
        ser.write(makeSerialString(next_melbands_val[index_mapping].tolist()))
        ser.flushInput()
        ser.flushOutput()
    time.sleep(0.05)

if ARDUINO:
    ser.write(makeSerialString(initialVals))
    ser.flushInput()
    ser.flushOutput()
# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio (7)
p.terminate()