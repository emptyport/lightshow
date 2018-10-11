import glob
import numpy as np
import librosa

TIME_DIFF = 0.041667
N_CHANNELS = 10

files_to_analyze = glob.glob("./wav/*.wav")

length = len(files_to_analyze)
print 'Analyzing',length,'audio files...'

count = 1
for file in files_to_analyze:
    print 'Processing file',count,'of',length,file
    #file = file.replace(" ", "\ ")
    print 'Reading...'
    y, sr = librosa.load(file)
    print 'Analyzing...'
    duration = librosa.core.get_duration(y, sr=sr)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    C = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr, n_chroma=N_CHANNELS)
    C = np.transpose(C)
    C = C.tolist()
    times = np.linspace(1/sr, duration, len(C))

    print 'Binning...'
    val_boxed = [C[0]]
    time_boxed = [times[0]]
    val_queue = []
    time_queue = []
    for i in range(1, len(C)):
        val_queue.append(C[i])
        time_queue.append(times[i])
        if times[i] - time_boxed[-1] > TIME_DIFF:
            val_boxed.append(np.mean(val_queue, axis=0))
            time_boxed.append((time_queue[-1] + time_queue[0])/2)
            val_queue = []
            time_queue = []
 
    print 'Normalizing...'
    for i in range(0, len(val_boxed)):
        lowerBound = i
        if lowerBound < 0:
            lowerBound = 0
        upperBound = i+1
        if upperBound > len(val_boxed):
            upperBound = len(val_boxed)
        maxVals = np.max(val_boxed[lowerBound:upperBound], axis=0)
        newVals = 255*np.asarray(val_boxed[i])/maxVals
        newVals = newVals.astype(int)
        val_boxed[i] = newVals

    time_filename = file.replace("./wav/", "./seq/").replace(".wav", ".times")
    data_filename = file.replace("./wav/", "./seq/").replace(".wav", ".dat")

    np.savetxt(time_filename, time_boxed, delimiter='', newline='\n')
    np.savetxt(data_filename, val_boxed, delimiter=',', newline='\n')
    print 'Finished'
