import pyaudio
import wave
import time
import numpy as np
import serial
import random

ARDUINO = True
N_CHANNELS = 10

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

def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

file = open('./playlist.txt', 'r')
song_names = file.readlines()

for song in song_names:
    # Write to Arduino to make sure the lights are off
    initialVals = []
    for i in range(0, N_CHANNELS):
        initialVals.append(0)
    if ARDUINO:
        ser.write(makeSerialString(initialVals))

    index_mapping = np.linspace(0, N_CHANNELS-1, N_CHANNELS).astype(int)

    audio_filename = './wav/'+song+'.wav'
    time_filename = './seq/'+song+'.times'
    data_filename = './seq/'+song+'.dat'
    onset_filename = './seq/'+song+'.onsets'

    onsets_file = open(onset_filename, 'r')
    onsets = onsets_file.readlines()
    times = np.loadtxt(time_filename).tolist()
    vals = list(np.loadtxt(data_filename, delimiter=','))

    wf = wave.open(audio_filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

    stream.start_stream()

    start_time = time.time()
    next_time = times.pop(0)
    next_val = vals.pop(0)
    next_onset = float(onsets.pop(0))
    shouldChange = True

    while stream.is_active():
        if time.time() - start_time >= next_onset:
            shouldChange = True
            try:
                next_onset = float(onsets.pop(0))
            except:
                dummy = 0

        if time.time() - start_time >= next_time:
            if shouldChange:
                mean_val = np.mean(next_val)
                prob_cutoff = 0.5 * mean_val / 255
                if prob_cutoff > random.random():
                    np.random.shuffle(index_mapping)
                    print 'Shuffling'
                print ' '.join(['%3.f']*len(next_val)) % tuple(next_val[index_mapping])
                if ARDUINO:
                    ser.write(makeSerialString(next_val[index_mapping].tolist()))
                    ser.flushInput()
                    ser.flushOutput()
                shouldChange = False
                try:
                    next_val = vals.pop(0)
                    next_time = times.pop(0)
                except:
                    dummy = 0
        time.sleep(0.001)

    if ARDUINO:
        ser.write(makeSerialString(initialVals))
        ser.flushInput()
        ser.flushOutput()

    stream.stop_stream()
    stream.close()
    wf.close()

    p.terminate()
