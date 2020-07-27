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

print writeReg(52,[0, 0, 0x20]) #Set en_sd
print writeReg(0x03, [0, 0, 30]) #Vmax
print writeReg(0x06, [0, 0, 20]) #Amax
print writeReg(0x02, [0, 0, 1]) #Vmin
print writeReg(0x00, [0, 0, 0])

print writeReg(0x13, [0, 0, 30])
print writeReg(0x16, [0, 0, 20])
print writeReg(0x12, [0, 0, 1])
print writeReg(0x10, [0, 0, 0])
sleep(1)

val = 0
while True:
    print readReg(1)
    print writeReg(0x00, [val >> 16, val >> 8, val])
    print writeReg(0x10, [val >> 16, val >> 8, val])
    val += 256
    sleep(0.3)
