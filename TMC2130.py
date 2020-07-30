import spidev
from time import sleep

class TMC2130():
    def __init__(self, spiDev, spiCh):
        spi = spidev.SpiDev()
        spi.open(spiDev, spiCh)
        spi0.max_speed_hz = 100000
        spi0.mode = 3
        spi0.no_cs = False

    def initialize(self):
        res = spi.xfer2([0x01, 0x00, 0x00, 0x00, 0x00])
        res = spi.xfer2([0x80, 0x00, 0x00, 0x00, 0x05])
        res = spi.xfer2([0x90, 0x00, 0x00, 0x10, 0x10])
        res = spi.xfer2([0xec, 0x32, 0x02, 0x80, 0x08])
        
    def writeReg(addr, data):
        pass
    
    def readReg(addr):
        pass

for i in [0x00, 0x01, 0x04, 0x12, 0x2d, 0x6b, 0x6c, 0x6f, 0x71, 0x73]:
    print "0x%02x:"%i,
    spi0.xfer2([i, 0, 0, 0, 0])
    result = spi0.xfer2([i, 0, 0, 0, 0])
    print ["0x%02x"%x for x in result]

while True:
    #res=spi.xfer2([0x01, 0x00, 0x00, 0x00, 0x00])
    #print ["0x%02x"%x for x in res]
    GPIO.output(18, False)
    GPIO.output(24, False)
    sleep(0.0001)
    GPIO.output(18, True)
    GPIO.output(24, True)
    sleep(0.0001)
