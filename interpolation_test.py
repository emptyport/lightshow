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

maxVal = np.max(mapped_val_boxed)
print maxVal
for i in range(0, len(mapped_val_boxed)):
    newVals = 255*mapped_val_boxed[i]/maxVal
    newVals = newVals.astype(int)
    mapped_val_boxed[i] = newVals
