DEBUG = True

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

    def __init__(self, spiDev, spiCh):
        if not DEBUG:
            self.spi = spidev.SpiDev()
            self.spi.open(spiDev, spiCh)
            self.spi.max_speed_hz = 100000
            self.spi.mode = 3
            self.spi.no_cs = False
        self.spiStatus = 0
        
    def initialize(self):
        #print writeReg(52,[0, 0, 0x20]) #Set en_sd
        self.writeReg(self.COMMON | self.IFCONFIG, self.IFCONFIG_ENSD)

    def writeReg(addr, data):
        if isinstance(data, int):
            intData = data
            data = [ (data >> 16)&0xff, (data >> 8)&0xff, data&0xff ]
        else:
            intData = (data[0]<<16) + (data[1]<<8) + data[2] 
        addr = addr << 1
        res = realXfer([addr]+data)
        self.spiStatus = res[0]

    def readReg(addr):
        addr = addr << 1
        addr |= 1
        res = realXfer([addr, 0, 0, 0])
        self.spiStatus = res[0]
        return (res[1]<<16) + (res[2]<<8) + (res[3])
        
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
        pass
        
    def home(self, motor):
        print "Homing..."
        #Get current switch state
        switch = self.getSwitch(motor)
            
        if switch:
            print "Switch started triggered. Moving off..."
            currentPos = readReg(motor | self.ACTUAL)
            print "Current position:", currentPos
            #Go forward some
            newPos = currentPos + 512
            writeReg(motor | self.TARGET, newPos)
            sleep(1)
            print "Current position:", readReg(motor | self.ACTUAL)
            #Recheck switch
            switch = self.getSwitch(motor)
            print "Switch is now", switch
        if not switch:
            #Assume we're at full-right position
            writeReg(motor | self.ACTUAL, 0x7fffff)
            #Prime X_Latched
            writeReg(motor | self.LATCHED, 0)
            #Head towards 0
            writeReg(motor | self.TARGET, 0)
            while not switch:
                switch = self.getSwitch(motor)
            print "Hit switch..."
            trigPos = readReg(motor | self.LATCHED)
            print "Triggered at", trigPos
            #Go to trigger position
            writeReg(motor | self.TARGET, trigPos)
            while not self.getOnTarget(motor):
                pass
            #set to 0
            writeReg(motor | self.ACTUAL, 0)



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
