import serial
from time import time
from utils import getkey
import matplotlib.pyplot as plt
import numpy as np

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

def plotInterval(X, start, end):
    plt.vlines(X[start],-5,5,linestyles='solid',colors='r',linewidth=3)
    plt.vlines(X[end],-5,5,linestyles='solid',colors='r',linewidth=3)

def slice(X, start, end):
    Xslice = X[start:end]
    # Xslice -= Xslice[0]
    return Xslice

def plotStem(y, expected=82, intrv=(0,-1), sr=2500):
    c = abs(np.fft.fft(y))
    n = len(y)
    c = c/n * 2
    freqs = np.linspace(0,sr,n)
    
    plt.figure(figsize=(25, 5), dpi=100)
    plt.stem(freqs[intrv[0]:intrv[1]], c[intrv[0]:intrv[1]])
    plt.xticks(np.arange(0,2500,100))
    plt.show()
    
    ind = np.argpartition(c[1:-n//2], -10)[-10:]
    print("Top 10: ", *sorted([round(indx/n * sr, 2) for indx in ind]))
    print("Expected", expected,'\n\n\n')