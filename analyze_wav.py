import glob
import numpy as np
import subprocess

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

TIME_DIFF = 0.041667
N_CHANNELS = 10
MA_WINDOW = 31
FADE_SECONDS = 5
FADE_FRAMES = int(FADE_SECONDS / TIME_DIFF)
BACK_NORMALIZE = 0
FORWARD_NORMALIZE = 40

files_to_analyze = glob.glob("./wav/*.wav")

length = len(files_to_analyze)
print 'Analyzing',length,'audio files...'

count = 1
for file in files_to_analyze:
    print 'Processing file',count,'of',length,file
    aubio_file = file.replace(" ", "\ ")

    print 'Melbands...'
    command = "aubio melbands "+aubio_file+" > ./tmp.txt"
    return_code = subprocess.call(command, shell=True)
    print 'Onsets...'
    command = "aubio onset "+aubio_file+" > "+aubio_file.replace("./wav/", "./seq/").replace(".wav", ".onsets")
    return_code = subprocess.call(command, shell=True)

    print 'Reading...'
    melband_file = open('./tmp.txt', 'r')
    melbands = melband_file.readlines()
    times = []
    vals = []
    for line in melbands:
        times.append(float(line.rstrip().split()[0]))

        rawVals = line.rstrip().split()[1:]
        arr = []
        for val in rawVals:
            arr.append(float(val))
        vals.append(np.asarray(arr))

    print 'Binning...'
    val_boxed = [vals[0]]
    time_boxed = [times[0]]
    val_queue = []
    time_queue = []
    for i in range(1, len(vals)):
        val_queue.append(vals[i])
        time_queue.append(times[i])
        if times[i] - time_boxed[-1] > TIME_DIFF:
            val_boxed.append(np.mean(val_queue, axis=0))
            time_boxed.append((time_queue[-1] + time_queue[0])/2)
            val_queue = []
            time_queue = []
    
    print 'Mapping...'
    x = np.linspace(0, 1, np.size(vals[0]))
    newX = np.linspace(0, 1, N_CHANNELS)
    mapped_vals = []
    for y in val_boxed:
        newY = np.interp(newX, x, y)
        mapped_vals.append(newY)

    print 'Smoothing...'
    for i in range(0, len(mapped_vals)):
        lowerBound = i-MA_WINDOW
        if lowerBound < 0:
            lowerBound = 0
        upperBound = i+MA_WINDOW
        if upperBound > len(mapped_vals):
            upperBound = len(mapped_vals)
        meanVal = np.mean(mapped_vals[lowerBound:upperBound], axis=0)
        mapped_vals[i] = meanVal

    print 'Normalizing...'
    for i in range(0, len(mapped_vals)):
        lowerBound = i-BACK_NORMALIZE
        if lowerBound < 0:
            lowerBound = 0
        upperBound = i+FORWARD_NORMALIZE
        if upperBound > len(mapped_vals):
            upperBound = len(mapped_vals)
        maxVals = np.max(mapped_vals[lowerBound:upperBound], axis=0)
        newVals = 255*np.asarray(mapped_vals[i])/maxVals
        newVals = newVals.astype(int)
        mapped_vals[i] = newVals

    print 'Fading...'
    start_vals = mapped_vals[len(mapped_vals)-FADE_FRAMES]
    steps = start_vals.astype(float) / FADE_FRAMES
    step = 1
    for i in range(len(mapped_vals)-FADE_FRAMES, len(mapped_vals)):
        mapped_vals[i] = (mapped_vals[i] - step * steps).astype(int)
        below_zero_indices = mapped_vals[i] < 0
        mapped_vals[i][below_zero_indices] = 0
        step += 1

    time_filename = file.replace("./wav/", "./seq/").replace(".wav", ".times")
    data_filename = file.replace("./wav/", "./seq/").replace(".wav", ".dat")

    np.savetxt(time_filename, time_boxed, delimiter='', newline='\n')
    np.savetxt(data_filename, mapped_vals, delimiter=',', newline='\n')
    print 'Finished'
