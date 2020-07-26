import spidev
from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

spi0 = spidev.SpiDev()
spi1 = spidev.SpiDev()

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

GPIO.output(12, True)
GPIO.output(23, True)
GPIO.output(18, True)
GPIO.output(25, True)
GPIO.output(24, True)

spi0.open(0, 0)
spi0.max_speed_hz = 100000
spi0.mode = 3
spi0.no_cs = False

spi1.open(0, 1)
spi1.max_speed_hz = 100000
spi1.mode = 3


res = spi0.xfer2([0x01, 0x00, 0x00, 0x00, 0x00])
res = spi0.xfer2([0x80, 0x00, 0x00, 0x00, 0x05])
res = spi0.xfer2([0x90, 0x00, 0x00, 0x10, 0x10])
res = spi0.xfer2([0xec, 0x32, 0x02, 0x80, 0x08])

res = spi1.xfer2([0x01, 0x00, 0x00, 0x00, 0x00])
res = spi1.xfer2([0x80, 0x00, 0x00, 0x00, 0x05])
res = spi1.xfer2([0x90, 0x00, 0x00, 0x10, 0x10])
res = spi1.xfer2([0xec, 0x32, 0x02, 0x80, 0x08])

#spi.xfer2([0,0,0,0,0])
for i in [0x00, 0x01, 0x04, 0x12, 0x2d, 0x6b, 0x6c, 0x6f, 0x71, 0x73]:
    print "0x%02x:"%i,
    spi0.xfer2([i, 0, 0, 0, 0])
    result = spi0.xfer2([i, 0, 0, 0, 0])
    print ["0x%02x"%x for x in result]

for i in [0x00, 0x01, 0x04, 0x12, 0x2d, 0x6b, 0x6c, 0x6f, 0x71, 0x73]:
    print "0x%02x:"%i,
    spi1.xfer2([i, 0, 0, 0, 0])
    result = spi1.xfer2([i, 0, 0, 0, 0])
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
