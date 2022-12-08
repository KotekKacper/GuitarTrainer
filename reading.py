import serial
import time

ser = serial.Serial('/dev/ttyUSB0', baudrate=230400)
time.sleep(3)

file = open("data.txt", 'w')
print("Start!")
while True:
    start = time.time()
    nr_of_readings = 0
    while True:
        nr_of_readings += 1
        data = ser.readline()
        file.writelines(str(data)[2:6]+"\n")
        stop = time.time()
        if stop-start >= 1.0:
            break

    print("Nr of readings: ", nr_of_readings)

file.close()