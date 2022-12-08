import serial
from time import time
from utils import getkey
import matplotlib.pyplot as plt

def readingSerialDataToFile(filename, port_addr="/dev/ttyUSB0", baudrate=230400):
    try:
        ser = serial.Serial(port_addr, baudrate)
    except:
        print("Error: couldn't connect to arduino")
        return
    
    time.sleep(3)

    file = open(filename, 'w')
    nr_of_readings = 0
    print("Start!\n(press 'space' to stop recording)")
    start = time.time()
    while True:
        data = ser.readline()
        file.writelines(str(data)[2:6]+"\n")

        nr_of_readings += 1
        stop = time.time()
        if stop-start >= 1.0:
            print("Nr of readings last second: ", nr_of_readings)
            nr_of_readings = 0
            start = time.time()
        if getkey() == 'space':
            break
    
    file.close()

def readFile(filename):
    file = open(filename, 'r')
    data = list()
    for line in file:
        data.append(float(line.rstrip()))
    return data

def plotRecording(y, start_point=0, end_point=-1):
    plt.plot(y[start_point:end_point])
    plt.show()
