import time
import serial
ser = serial.Serial('/dev/ttyACM0', 57600)

vals = [0,0,0,0,0,0,0,0,0,0]

def makeSerialString(arr):
    s = "<"
    for val in arr:
        s += str(val).zfill(3)
        s += ":"
    s = s[:-1]
    s += ">"
    return s
    
ser.write(makeSerialString(vals))

while True:
    while vals[0] < 255:
        for i in range(0, len(vals)):
            vals[i] += 1
        ser.write(makeSerialString(vals))
        time.sleep(0.1)
    vals = [0,0,0,0,0,0,0,0,0,0]
