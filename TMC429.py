DEBUG = True

import logging
if not DEBUG:
    import spidev
from time import sleep

class TMC429():

    MOTOR1 = 0
    MOTOR2 = 16
    MOTOR3 = 32
    COMMON = 48
    
    TARGET  = 0
    ACTUAL  = 1
    VMIN    = 2
    VMAX    = 3
    VTARGET = 4
    VACTUAL = 5
    AMAX    = 6
    AACTUAL = 7
    ATHRESH = 8
    DECCEL  = 9
    REFCONF = 10
    INTCONF = 11
    ACCEL   = 12
    DXREFTOL= 13
    LATCHED = 14
    USTEP   = 15
    
    DGLOW   = 0
    DGHIGH  = 1
    COVER   = 2
    COVERDG = 3
    IFCONFIG= 4
    POSCOMP = 5
    PCINT   = 6
    RESVD   = 7
    PWRDN   = 8 
    VERSION = 9
    RESVD   = 10
    RESVD   = 11
    RESVD   = 12
    RESVD   = 13
    RESVD   = 14
    CONFIG  = 15
    
    IFCONFIG_INVREF     = 1
    IFCONFIG_SDOINT     = 2
    IFCONFIG_STEPHALF   = 4
    IFCONFIG_INVSTEP    = 8
    IFCONFIG_INVDIR     = 16
    IFCONFIG_ENSD       = 32
    IFCONFIG_POSCOMP0   = 64
    IFCONFIG_POSCOMP1   = 128
    IFCONFIG_ENREFR     = 256

    def __init__(self, spiDev, spiCh, name="TMC429"):
        if not DEBUG:
            self.spi = spidev.SpiDev()
            self.spi.open(spiDev, spiCh)
            self.spi.max_speed_hz = 100000
            self.spi.mode = 3
            self.spi.no_cs = False
        self.spiStatus = 0
        self.logger = logging.getLogger(name)
        self.STOP = False
        self.loopCounter = 0
        
        self.isMoving = False
        self.isHoming = False
        self.isHomed = False
        self.m1pos = None
        self.m2pos = None
        self.m3pos = None
        self.m1OnTarget = False
        self.m2OnTarget = False
        self.m3OnTarget = False
        
    def initialize(self):
        #print writeReg(52,[0, 0, 0x20]) #Set en_sd
        self.writeReg(self.COMMON | self.IFCONFIG, self.IFCONFIG_ENSD)

    def writeReg(self, addr, data):
        if isinstance(data, int):
            intData = data
            data = [ (data >> 16)&0xff, (data >> 8)&0xff, data&0xff ]
        else:
            intData = (data[0]<<16) + (data[1]<<8) + data[2] 
        self.logger.debug("Sending 0x%0.6x to 0x%0.2x"%(intData, addr))
        addr = addr << 1
        if not DEBUG:
            res = self.spi.xfer2([addr]+data)
        else:
            res = [0, 0, 0, 0]
        self.spiStatus = res[0]

    def readReg(self, addr):
        origAddr = addr
        addr = addr << 1
        addr |= 1
        if not DEBUG:
            res = self.spi.xfer2([addr, 0, 0, 0])
        else:
            res = [0, 0, 0, 0]
        self.spiStatus = res[0]
        val = (res[1]<<16) + (res[2]<<8) + (res[3])
        self.logger.debug("0x%0.2x is 0x%0.6x. SPI status is 0x%0.2x."%(origAddr, val, self.spiStatus))
        return val
        
    def getInt(self):
        return (self.spiStatus>>7)&1 == 1
    def getCDGW(self):
        return (self.spiStatus>>6)&1 == 1
    def getRS3(self):
        return (self.spiStatus>>5)&1 == 1
    def getEQT3(self):
        return (self.spiStatus>>4)&1 == 1
    def getRS2(self):
        return (self.spiStatus>>3)&1 == 1
    def getEQT2(self):
        return (self.spiStatus>>2)&1 == 1
    def getRS1(self):
        return (self.spiStatus>>1)&1 == 1
    def getEQT1(self):
        return self.spiStatus&1 == 1
        
    def setVMin(self, motor, vmin):
        self.writeReg(motor | self.VMIN, vmin)
    def setVMax(self, motor, vmax):
        self.writeReg(motor | self.VMAX, vmax)
    def setAMax(self, motor, amax):
        self.writeReg(motor | self.AMAX, amax)
        
    def getSwitch(self, motor):
        readReg(motor | self.ACTUAL) #Make sure spiStatus is updated
        if motor == self.MOTOR1:
            return self.getRS1()
        elif motor == self.MOTOR2:
            return self.getRS2()
        elif motor == self.MOTOR3:
            return self.getRS3()
        else:
            #Bad input
            return None
            
    def getOnTarget(self, motor):
        readReg(motor | self.ACTUAL) #Make sure spiStatus is updated
        if motor == self.MOTOR1:
            return self.getEQT1()
        elif motor == self.MOTOR2:
            return self.getEQT2()
        elif motor == self.MOTOR3:
            return self.getEQT3()
        else:
            #Bad input
            return None
        
    def run(self):
        while True:
            self.m1pos = self.readReg(self.MOTOR1 | self.ACTUAL)
            self.m2pos = self.readReg(self.MOTOR2 | self.ACTUAL)
            self.m3pos = self.readReg(self.MOTOR3 | self.ACTUAL)
            self.m1OnTarget = self.getEQT1()
            self.m2OnTarget = self.getEQT2()
            self.m3OnTarget = self.getEQT3()
            if self.isHoming:
                self.home()
            if self.STOP:
                self.logger.critical("Received STOP signal")
                break
            self.loopCounter += 1
            sleep(0.1)
        
    def home(self, motor):
        self.logger.info("Homing...")
        self.isHoming = True
        self.isHomed = False
        
        #Get current switch state
        switch = self.getSwitch(motor)
            
        if switch:
            self.logger.debug("Switch started triggered. Moving off...")
            currentPos = readReg(motor | self.ACTUAL)
            self.logger.debug("Current position:", currentPos)
            #Go forward some
            newPos = currentPos + 512
            writeReg(motor | self.TARGET, newPos)
            sleep(0.5)
            self.logger.debug("Current position:", readReg(motor | self.ACTUAL))
            #Recheck switch
            switch = self.getSwitch(motor)
            self.logger.debug("Switch is now %r"%switch)
        if not switch:
            #Get current position to calculate error
            currentPos = readReg(motor | self.ACTUAL)
            #Assume we're at full-right position
            writeReg(motor | self.ACTUAL, 0x7fffff)
            #Prime X_Latched
            writeReg(motor | self.LATCHED, 0)
            #Head towards 0
            writeReg(motor | self.TARGET, 0)
            while not switch:
                switch = self.getSwitch(motor)
                sleep(0.1)
            self.logger.debug("Hit switch...")
            trigPos = readReg(motor | self.LATCHED)
            self.logger.debug("Triggered at %d"%trigPos)
            #Go to trigger position
            writeReg(motor | self.TARGET, trigPos)
            while not self.getOnTarget(motor):
                sleep(0.1)
            #set to 0
            writeReg(motor | self.ACTUAL, 0)
            homingError = (0x7fffff - trigPos) - currentPos
            self.logger.info("Homing error: %d"%homingError)
            self.isHomed = True
            self.isHoming = False



#print writeReg(0x03, [0, 0, 30]) #Vmax
#writeReg(self.MOTOR1 | self.VMAX, 30)

#print writeReg(0x06, [0, 0, 20]) #Amax
#writeReg(self.MOTOR1 | self.AMAX, 20)

#print writeReg(0x02, [0, 0, 1]) #Vmin
#writeReg(self.MOTOR1 | self.VMIN, 1)

#print writeReg(0x00, [0, 0, 0])
#writeReg(self.MOTOR1 | self.TARGET, 0)



#print writeReg(0x03, [0, 0, 30]) #Vmax
#writeReg(self.MOTOR2 | self.VMAX, 30)

#print writeReg(0x06, [0, 0, 20]) #Amax
#writeReg(self.MOTOR2 | self.AMAX, 20)

#print writeReg(0x02, [0, 0, 1]) #Vmin
#writeReg(self.MOTOR2 | self.VMIN, 1)

#print writeReg(0x00, [0, 0, 0])
#writeReg(self.MOTOR2 | self.TARGET, 0)

#val = 0
#while True:
#    print readReg(1)
#    print writeReg(0x00, [val >> 16, val >> 8, val])
#    print writeReg(0x10, [val >> 16, val >> 8, val])
#    val += 256
#    sleep(0.3)
