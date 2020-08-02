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

print writeReg(52,[0, 0, 0x30]) #Set en_sd, invert direction
print writeReg(0x03, [0, 0, 30]) #Vmax
print writeReg(0x06, [0, 0, 20]) #Amax
print writeReg(0x02, [0, 0, 1]) #Vmin
print writeReg(0x00, [0, 0, 0])

print writeReg(0x13, [0, 0, 30])
print writeReg(0x16, [0, 0, 20])
print writeReg(0x12, [0, 0, 1])
print writeReg(0x10, [0, 0, 0])
sleep(1)

def home():
    print "Homing..."
    #Get current switch state
    switch = ( (readReg(1)[0] & 2) != 0 )
    if switch:
        print "Switch started triggered. Moving off..."
        currentPos = readReg(1)
        currentPos = (currentPos[1] << 16) + (currentPos[2] << 8) + (currentPos[3])
        print "Position:", currentPos
        #Go forward some
        newPos = currentPos + 512
        writeReg(0x00, [newPos >> 16, newPos >> 8, newPos])
        sleep(1)
        print "Position:", readReg(1)
        #Recheck switch
        switch = ( (readReg(1)[0] & 2) != 0 )
        print "Switch is now", switch
    if not switch:
        #Assume we're at full-right position
        writeReg(1, [0x0f, 0xff, 0xff])
        #Prime X_Latched
        writeReg(14, [0, 0, 0])
        #Head towards 0
        writeReg(0x00, [0, 0, 0])
        while not switch:
            switch = ( (readReg(1)[0] & 2) != 0 )
        print "Hit switch..."
        trigPos = readReg(14)
        print "Triggered at", trigPos
        #Go to trigger position
        writeReg(0, [trigPos[1], trigPos[2], trigPos[3]])
        sleep(1)
        #set to 0
        writeReg(1, [0, 0, 0])


val = 0
while True:
    home()
    while val < 2048:
        print "Register 1:", readReg(1)
        writeReg(0x00, [val >> 16, val >> 8, val])
        writeReg(0x10, [val >> 16, val >> 8, val])
        val += 128
        sleep(0.1)
    while val > 0:
        print "Register 1:", readReg(1)
        writeReg(0x00, [val >> 16, val >> 8, val])
        writeReg(0x10, [val >> 16, val >> 8, val])
        val -= 128
        sleep(0.1)
