import spidev
from time import sleep

class TMC2130():
    GCONF       = 0x00
    GSTAT       = 0x01
    IOIN        = 0x04
    IHOLD_IRUN  = 0x10
    TPOWERDOWN  = 0x11
    TSTEP       = 0x12
    TPWMTHRS    = 0x13
    TCOOLTHRS   = 0x14
    THIGH       = 0x15
    XDIRECT     = 0x2d
    VDCMIN      = 0x33
    MSLUT0      = 0x60
    MSLUT1      = 0x61
    MSLUT2      = 0x62
    MSLUT3      = 0x63
    MSLUT4      = 0x64
    MSLUT5      = 0x65
    MSLUT6      = 0x66
    MSLUT7      = 0x67
    MSLUTSEL    = 0x68
    MSLUTSTART  = 0x69
    MSCNT       = 0x6a
    MSCURACT    = 0x6b
    CHOPCONF    = 0x6c
    COOLCONF    = 0x6d
    DCCTRL      = 0x6e
    DRV_STATUS  = 0x6f
    PWMCONF     = 0x70
    PWM_SCALE   = 0x71
    ENCM_CTRL   = 0x72
    LOST_STEPS  = 0x73
    
    READABLE = [self.GCONF, self.GSTAT, self.IOIN, self.TSTEP, self.XDIRECT, self.MSCNT, self.MSCURACT, self.CHOPCONF, self.DRV_STATUS, self.PWM_SCALE, self.LOST_STEPS]
    

    def __init__(self, spiDev, spiCh):
        spi = spidev.SpiDev()
        spi.open(spiDev, spiCh)
        spi0.max_speed_hz = 100000
        spi0.mode = 3
        spi0.no_cs = False
        self.spiStatus = 0

    def initialize(self):
        #res = spi.xfer2([0x01, 0x00, 0x00, 0x00, 0x00])
        self.readReg(self.GSTAT)
        #res = spi.xfer2([0x80, 0x00, 0x00, 0x00, 0x05])
        self.writeReg(self.GCONF, 0x00000005)
        #res = spi.xfer2([0x90, 0x00, 0x00, 0x10, 0x10])
        self.writeReg(self.IHOLD_IRUN, 0x00001010)
        #res = spi.xfer2([0xec, 0x32, 0x02, 0x80, 0x08])
        self.writeReg(self.CHOPCONF, 0x32028080)
        
    def writeReg(addr, data):
        addr |= 0b10000000
        if isinstance(data, int):
            data = [ (data >> 24)&0xff, (data >> 16)&0xff, (data >> 8)&0xff, data&0xff ]
        print "Writing %s to 0x%02x"%(', '.join(["0x%02x"%x for x in data]), addr)
        res = spi.xfer2([addr] + data)
        self.spiStatus = res[0]
    
    def readReg(addr):
        addr &= 0b01111111
        #Dummy read to set address
        print "Sending [0x%02x, 0, 0, 0]"%addr
        spi.xfer2([addr, 0, 0, 0, 0])
        res = spi.xfer2([addr, 0, 0, 0, 0])
        self.spiStatus = res[0]
        return (res[1] << 24) | (res[2] << 16) | (res[3] << 8) | (res[4])
        
    def getStandstill(self):
        return (self.spiStatus >> 3)&1 == 1
       
    def getSG2(self):
        return (self.spiStatus >> 2)&1 == 1
    
    def getDriverError(self):
        return (self.spiStatus >> 1)&1 == 1
        
    def getStandstill(self):
        return self.spiStatus&1 == 1
        
    def readAll(self)
        res = {}
        for addr in self.READABLE:
            res[addr] = self.readReg(addr)
        return res
