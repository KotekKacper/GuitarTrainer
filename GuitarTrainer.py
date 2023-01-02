import serial
import time
from utils import getkey
import matplotlib.pyplot as plt
import numpy as np
import json
import vlc

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
    if len(top10) < 1: top10 = [0]
    # print(top10)
    last_value = top10[0]
    peak_count = 1
    peak_sum = top10[0]
    for id in top10:
        if id == last_value+5.0:
            peak_count += 1
            peak_sum += id
            last_value+=5.0
    calculated = peak_sum/peak_count
    
    if expected != 0:
        print("Max          : ", maximum)
        print("Calculated   : ", calculated)
        print("Expected     : ", expected)
        print()
    
    return calculated

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

def getNote(y, srate=2500):
    values = abs(np.fft.fft(y))
    n = len(y)
    values = values/n * 2
    return noteClassification(values, 0, n, srate)


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

def giveFretFreqIntervals(conv_file):
    freqs = fillAllFrets(readConvertion(conv_file))
    intervals = dict()
    for k,v in freqs.items():
        string, fret = k.split('.')
        if k == "1.0":
            linterv = "78"
            rinterv = freqs[string+'.'+str(int(fret)+1)]
        elif k == "6.19":
            linterv = freqs[string+'.'+str(int(fret)-1)]
            rinterv = "1100"
        elif fret == '0':
            if string == '5':
                linterv = freqs[str(int(string)-1)+'.'+str(int(fret)+3)]
                rinterv = freqs[string+'.'+str(int(fret)+1)]
            else:
                linterv = freqs[str(int(string)-1)+'.'+str(int(fret)+4)]
                rinterv = freqs[string+'.'+str(int(fret)+1)]
        elif fret == '19':
            if string == '4':
                linterv = freqs[string+'.'+str(int(fret)-1)]
                rinterv = freqs[str(int(string)+1)+'.'+str(int(fret)-3)]
            else:
                linterv = freqs[string+'.'+str(int(fret)-1)]
                rinterv = freqs[str(int(string)+1)+'.'+str(int(fret)-4)]
        else:
            linterv = freqs[string+'.'+str(int(fret)-1)]
            rinterv = freqs[string+'.'+str(int(fret)+1)]
        intervals[k] = (int(v)-(int(v)-int(linterv))/2, int(v)+(int(rinterv)-int(v))/2)
    return intervals

def readGTIN(filename):
    tempo = 0
    data = list()
    with open(filename) as file:
        for line in file:
            line = line.rstrip()
            # avoiding comments and blanks
            if line.startswith('#') or line == '':
                continue
            if tempo == 0:
                tempo = float(line)
                continue

            duration, note = line.split(' ')
            data.append((duration, note))

    return (tempo, data)

def playGTIN(tempo, data):
    full_note_dur = 4*(60/tempo)

    for duration, note in data:
        start = time.time()
        duration = duration.split('/')
        note = note.split('.')

        print(note)
        
        display_time = full_note_dur*int(duration[0])/int(duration[1])
        while(time.time()-start < display_time):
            pass

def generateTabs(data):
    strings = {'1':[], '2':[], '3':[],
             '4':[], '5':[], '6':[]}
    for duration, note in data:
        duration = duration.split('/')
        note = note.split('.')

        for string, fret in strings.items():
            if string == note[0]:
                fret.append(note[1])
            else:
                fret.append('-')
        
        for i in range(32*int(duration[0])//int(duration[1])-1):
            for string, fret in strings.items():
                fret.append('-')
    
    # for i in range(50, 1000):
    #     print(strings['6'][i:i+20])
    #     print(strings['5'][i:i+20])
    #     print(strings['4'][i:i+20])
    #     print(strings['3'][i:i+20])
    #     print(strings['2'][i:i+20])
    #     print(strings['1'][i:i+20])
    #     time.sleep(0.1)

    return strings
    
def playTabs(tabs, tempo, width=21):
    full_note_dur = 4*(60/tempo)

    for i in range(0,len(tabs['1'])-width):
        start = time.time()
        lines = list()

        # progress bar
        curr_progress = i/(len(tabs['1'])-width)
        progress_signs = int(curr_progress*(width-2))+1
        lines.append('[' + '*'*progress_signs +
                     ' '*(width-2-progress_signs) + ']')

        # tabs
        for string_nr in range(6,0,-1):
            current = tabs[str(string_nr)][i:i+width]
            lines.append(''.join(current))

        print('\n'.join(lines))
        while(time.time()-start < full_note_dur/32):
            pass

def playSong(filename):
    music_file = vlc.MediaPlayer(filename)
    music_file.play()

if __name__ == "__main__":
    tempo, data = readGTIN("./songs/DoIWannaKnow.gtin")
    tabs = generateTabs(data)
    playSong("./songs/DoIWannaKnow.mp3")
    playTabs(tabs, tempo)
    # playGTIN(tempo, data)