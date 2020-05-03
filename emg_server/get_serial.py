import serial
import time

def read_from_arduino():
    line = ''
    with serial.Serial('/dev/cu.usbmodem1411', 9600, timeout=1) as ser:
        line = ser.readline()   # read a '\n' terminated line
        line = line.strip().decode("utf-8")
    try:
        return int(line)
    except:
        pass

def read_for_sec_to_array(n_sec=1):
    t_end = time.time() + n_sec
    arr = []
    while time.time() < t_end:
        val = read_from_arduino()
        if val != None:
            arr.append(val)
    return arr

