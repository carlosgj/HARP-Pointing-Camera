import logging
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
    
    READABLE = [GCONF, GSTAT, IOIN, TSTEP, XDIRECT, MSCNT, MSCURACT, CHOPCONF, DRV_STATUS, PWM_SCALE, LOST_STEPS]
    
    shadowregs = [0]*0x72

    def __init__(self, spiDev, spiCh, name="TMC2130"):
        self.spi = spidev.SpiDev()
        self.spi.open(spiDev, spiCh)
        self.spi.max_speed_hz = 100000
        self.spi.mode = 3
        self.spi.no_cs = False
        self.spiStatus = 0
        self.logger = logging.getLogger(name)
        self.STOP = False

    def initialize(self):
        #res = spi.xfer2([0x01, 0x00, 0x00, 0x00, 0x00])
        self.readReg(self.GSTAT)
        #res = spi.xfer2([0x80, 0x00, 0x00, 0x00, 0x05])
        self.writeReg(self.GCONF, 0x00000005)
        #res = spi.xfer2([0x90, 0x00, 0x00, 0x10, 0x10])
        self.writeReg(self.IHOLD_IRUN, 0x00001010)
        #res = spi.xfer2([0xec, 0x32, 0x02, 0x80, 0x08])
        self.writeReg(self.CHOPCONF, 0x32028080)
        
    def writeReg(self, addr, data):
        addr |= 0b10000000
        if isinstance(data, int):
            intData = data
            data = [ (data >> 24)&0xff, (data >> 16)&0xff, (data >> 8)&0xff, data&0xff ]
        else:
            intData = (data[0]<<24) + (data[1]<<16) + (data[2]<<8) + data[3] 
        self.logger.debug("Writing %s to 0x%02x"%(', '.join(["0x%02x"%x for x in data]), addr))
        res = self.spi.xfer2([addr] + data)
        self.spiStatus = res[0]
        self.shadowregs[addr] = intData 
    
    def readReg(self, addr):
        addr &= 0b01111111
        #Dummy read to set address
        self.logger.debug("Sending [0x%02x, 0, 0, 0]"%addr)
        self.spi.xfer2([addr, 0, 0, 0, 0])
        res = self.spi.xfer2([addr, 0, 0, 0, 0])
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
        
    def getVersion(self):
        ioin = self.readReg(self.IOIN)
        return (ioin >> 24) & 255
        
    def readAll(self):
        res = {}
        for addr in self.READABLE:
            res[addr] = self.readReg(addr)
        return res
        
    def run(self):
        while True:
            sleep(0.1)
            if self.STOP:
                self.logger.critical("Received STOP signal")
                break
