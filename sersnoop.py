import serial
import time

ser1 = serial.Serial('COM5', 115200, timeout=1)
ser2 = serial.Serial('COM6', 115200, timeout=1)

while True:
    try:
        delay = True
        if ser1.in_waiting:
            c1 = ser1.read(1)
            print "1>%02x"%ord(c1)
            ser2.write(c1)
            delay = False
        if ser2.in_waiting:
            c2 = ser2.read(1)
            print "2>%02x"%ord(c2)
            ser1.write(c2)
            delay = False
        if delay:
            time.sleep(0.1)
    except KeyboardInterrupt:
        ser1.close()
        ser2.close()
        break
    except:
        ser1.close()
        ser2.close()
        raise