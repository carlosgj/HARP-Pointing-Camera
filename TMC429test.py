import spidev
from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

spi = spidev.SpiDev()

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

GPIO.output(12, True)

spi.open(0, 0)
spi.max_speed_hz = 100000
spi.mode = 3
spi.no_cs = True

def realXfer(data):
    GPIO.output(12, False)
    res = spi.xfer2(data)
    GPIO.output(12, True)
    return res

def writeReg(addr, data):
    addr = addr << 1
    res = realXfer([addr]+data)
    return res[0]

def readReg(addr):
    addr = addr << 1
    addr |= 1
    res = realXfer([addr, 0, 0, 0])
    return res

for i in range(64):
    print i, ["0x%02x"%x for x in readReg(i)]

print writeReg(52, [0, 0, 0x20]) #Set en_sd
print writeReg(3, [0,0,50]) #Vmax
print writeReg(6, [0, 0, 5]) #Amax
print writeReg(2, [0, 0, 1]) #Vmin
print writeReg(0, [0, 0, 0])

while True:
    print readReg(1)
    print "Going to max"
    print writeReg(0, [0, 8, 255])
    sleep(3)
    print readReg(1)
    print "Going to 0"
    print writeReg(0, [0, 0, 1])
    sleep(3)
