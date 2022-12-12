import serial
from time import time
from utils import getkey
import matplotlib.pyplot as plt
import numpy as np
import json

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
    plt.figure(figsize=(25, 5), dpi=100)
    plt.plot(y[start_point:end_point])
    plt.show()

def plotInterval(X, start, end):
    plt.vlines(X[start],-5,5,linestyles='solid',colors='r',linewidth=3)
    plt.vlines(X[end],-5,5,linestyles='solid',colors='r',linewidth=3)

def slice(X, start, end):
    Xslice = X[start:end]
    # Xslice -= Xslice[0]
    return Xslice

def noteClassification(values, expected, n, srate):
    # indexes and values are mixed, they should be connected somehow
    ind = np.argpartition(values[:-n//2], -10)[-10:]
    top = {}

    for i in sorted(ind):
        top[round(i/n*srate,2)] = values[i]
        #print(i, i/n*srate, values[i])
    avg = sum([top[v] for v in top])/len(top)
    maximum = round(np.argmax(values[:-n//2])/n * srate, 2)

    # cut values that are smaller than the average and not close to possible dominant frequency point
    # no neighbours (-5.0 or +5.0)
    to_del = []
    for k in top:
        if not (k+5.0 in top or k-5.0 in top) and top[k] < avg:
            to_del.append(k)
    
    for el in to_del:
        del top[el]
    
    top10 = [value for value in top if value > 50.0]
    print(top10)
    last_value = top10[0]
    peak_count = 1
    peak_sum = top10[0]
    for id in top10:
        if id == last_value+5.0:
            peak_count += 1
            peak_sum += id
            last_value+=5.0
    calculated = peak_sum/peak_count
    
    print("Max          : ", maximum)
    print("Calculated   : ", calculated)
    print("Expected     : ", expected)
    print()

def plotStem(y, expected, srate=2500):
    values = abs(np.fft.fft(y))
    n = len(y)
    values = values/n * 2
    freqs = np.linspace(0,srate,n)
    
    plt.figure(figsize=(25, 5), dpi=100)
    plt.stem(freqs, values)
    plt.xticks(np.arange(0,2500,100))
    plt.show()
    
    noteClassification(values, expected, n, srate)

def readConvertion(filename):
    return json.load(open(filename))["pos-to-freq"]

def fillAllFrets(convertion):
    for string in range(6,0,-1):
        for fret in range(19,-1,-1):
            comb = str(string)+"."+str(fret)
            if comb not in convertion:
                if string == 4:
                    convertion[comb] = convertion[str(string+1)+"."+str(fret-4)]
                else:
                    convertion[comb] = convertion[str(string+1)+"."+str(fret-5)]
    return convertion
            
def giveFretFreqs(conv_file):
    return fillAllFrets(readConvertion(conv_file))