import logging
try:
    import spidev
except ImportError:
    import mockSpidev as spidev
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
    
    M1_BORESIGHT_MICROSTEPS = 2304
    M2_BORESIGHT_MICROSTEPS = 3071

    def __init__(self, spiDev, spiCh, name="TMC429", MRES=2, steps=200):
        self.spi = spidev.SpiDev()
        self.spi.open(spiDev, spiCh)
        self.spi.max_speed_hz = 100000
        self.spi.mode = 3
        self.spi.no_cs = False
        self.spiStatus = 0
        self.logger = logging.getLogger(name)
        self.STOP = False
        self.loopCounter = 0
        
        self.MRES = MRES
        self.steps_per_rev = steps
        self.microsteps_per_step = 256/(2**self.MRES)
        self.microsteps_per_rev = self.microsteps_per_step * self.steps_per_rev
        self.degrees_per_microstep = 360. / self.microsteps_per_rev
        self.microsteps_per_degree = self.microsteps_per_rev / 360.
        
        self.m1Homing = False
        self.m2Homing = False
        self.m1Homed = False
        self.m2Homed = False
        self.m1pos = None
        self.m2pos = None
        self.m1OnTarget = False
        self.m2OnTarget = False
        
    def motorName(self, motor):
        if motor == self.MOTOR1:
            return "MOTOR1"
        elif motor == self.MOTOR2:
            return "MOTOR2"
        elif motor == self.MOTOR3:
            return "MOTOR3"
        else:
            return "Invalid Motor"
        
    def initialize(self):
        """Initialize registers to common values"""
        #print writeReg(52,[0, 0, 0x20]) #Set en_sd
        self.writeReg(self.COMMON | self.IFCONFIG, self.IFCONFIG_ENSD)
        self.logger.info("Version: 0x%x"%self.getVersion())
        self.writeReg(self.MOTOR1 | self.ACTUAL, 0)
        self.writeReg(self.MOTOR1 | self.TARGET, 0)
        self.writeReg(self.MOTOR2 | self.ACTUAL, 0)
        self.writeReg(self.MOTOR2 | self.TARGET, 0)

    def writeReg(self, addr, data):
        if isinstance(data, int):
            intData = data
            data = [ (data >> 16)&0xff, (data >> 8)&0xff, data&0xff ]
        else:
            intData = (data[0]<<16) + (data[1]<<8) + data[2] 
        #self.logger.debug("Sending 0x%0.6x to 0x%0.2x"%(intData, addr))
        addr = addr << 1
        res = self.spi.xfer2([addr]+data)
        self.spiStatus = res[0]

    def readReg(self, addr):
        origAddr = addr
        addr = addr << 1
        addr |= 1
        res = self.spi.xfer2([addr, 0, 0, 0])
        self.spiStatus = res[0]
        val = (res[1]<<16) + (res[2]<<8) + (res[3])
        #self.logger.debug("0x%0.2x is 0x%0.6x. SPI status is 0x%0.2x."%(origAddr, val, self.spiStatus))
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
        
    def getTargetSteps(self, motor):
        """Gets the target in uncorrected microsteps
        i.e. the value of TARGET
        """
        return self.readReg(motor | self.TARGET)
    
    def getActualSteps(self, motor):
        """Gets the position in uncorrected microsteps
        i.e. the value of ACTUAL
        """
        return self.readReg(motor | self.ACTUAL)
        
    def getTargetDegrees(self, motor):
        """Gets the target in degrees-off-boresight
        """
        if motor == self.MOTOR1:
            return (self.getTargetSteps(motor) - self.M1_BORESIGHT_MICROSTEPS) * self.degrees_per_microstep
        elif motor == self.MOTOR2:
            return (self.getTargetSteps(motor) - self.M2_BORESIGHT_MICROSTEPS) * self.degrees_per_microstep
            
    def getActualDegrees(self, motor):
        """Gets the current position in degrees-off-boresight
        """
        if motor == self.MOTOR1:
            return (self.getActualSteps(motor) - self.M1_BORESIGHT_MICROSTEPS) * self.degrees_per_microstep
        elif motor == self.MOTOR2:
            return (self.getActualSteps(motor) - self.M2_BORESIGHT_MICROSTEPS) * self.degrees_per_microstep
        
    def setVMin(self, motor, vmin):
        """Sets minimum velocity parameter"""
        self.writeReg(motor | self.VMIN, vmin)

    def setVMax(self, motor, vmax):
        """Sets maximum velocity parameter"""
        self.writeReg(motor | self.VMAX, vmax)

    def setAMax(self, motor, amax):
        """Sets maximum acceleration parameter"""
        self.writeReg(motor | self.AMAX, amax)
        
    def setTargetRawSteps(self, motor, target):
        """Sets the target in raw steps (the value of TARGET)

        This is uncorrected for reference switch location.
        """
        if (motor == self.MOTOR1 and self.m1Homing) or (motor==self.MOTOR2 and self.m2Homing):
            return
        self.writeReg(motor | self.TARGET, target)
    
    def setTargetStepsCalibrated(self, motor, steps):
        """Sets the target in microsteps-off-boresight
        """
        if motor == self.MOTOR1:
            self.setTargetRawSteps(motor, steps + self.M1_BORESIGHT_MICROSTEPS)
        elif motor == self.MOTOR2:
            self.setTargetRawSteps(motor, steps + self.M2_BORESIGHT_MICROSTEPS)
    
    def setTargetDegrees(self, motor, degrees):
        """Sets the target in degrees-off-boresight
        """
        self.setTargetStepsCalibrated(motor, degrees * self.microsteps_per_degree)
        
    def getSwitch(self, motor):
        """Returns the state of the limit switch

        Left-side (default) limit switch/reference for the given motor
        """
        self.getActualSteps(motor) #Make sure spiStatus is updated
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
        """Returns True if the given motor is on target

        i.e. if ACTUAL == TARGET
        """
        self.getActualSteps(motor) #Make sure spiStatus is updated
        if motor == self.MOTOR1:
            return self.getEQT1()
        elif motor == self.MOTOR2:
            return self.getEQT2()
        elif motor == self.MOTOR3:
            return self.getEQT3()
        else:
            #Bad input
            return None
            
    def getVersion(self):
        """Returns the value of the VERSION register"""
        return self.readReg(self.COMMON | self.VERSION)
        
    def run(self):
        while True:
            if self.STOP:
                self.logger.critical("Received STOP signal")
                break
            self.m1pos = self.getActualDegrees(self.MOTOR1)
            self.m2pos = self.getActualDegrees(self.MOTOR1)
            self.m1OnTarget = self.getEQT1()
            self.m2OnTarget = self.getEQT2()
            if self.m1Homing:
                self.home(self.MOTOR1)
            elif self.m2Homing:
                self.home(self.MOTOR2)
            self.loopCounter += 1
            sleep(0.1)
        
    def home(self, motor):
        """ Homes the given motor.
        Leaves the motor in the 0 (far-left) position
        """
        self.logger.info("Homing %s..."%self.motorName(motor))
        if motor == self.MOTOR1:
            self.m1Homing = True
            self.m1Homed = False
        elif motor == self.MOTOR2:
            self.m2Homing = True
            self.m2Homed = False
        elif motor == self.MOTOR3:
            self.m3Homing = True
            self.m3Homed = False
        #Get current switch state
        switch = self.getSwitch(motor)
            
        if switch:
            self.logger.info("Switch started triggered. Moving off...")
            currentPos = self.getActualSteps(motor)
            self.logger.debug("Current position: %d"%currentPos)
            #Go forward some
            newPos = currentPos + 512
            self.writeReg(motor | self.TARGET, newPos)
            sleep(0.5)
            self.logger.debug("Current position: %d"%self.getActualSteps(motor))
            #Recheck switch
            switch = self.getSwitch(motor)
            self.logger.debug("Switch is now %r"%switch)
        if not switch:
            #Get current position to calculate error
            currentPos = self.getActualSteps(motor)
            #Assume we're at full-right position
            self.writeReg(motor | self.ACTUAL, 0x7fffff)
            #Prime X_Latched
            self.writeReg(motor | self.LATCHED, 0)
            #Head towards 0
            self.writeReg(motor | self.TARGET, 0)
            while not switch:
                switch = self.getSwitch(motor)
                sleep(0.01)
                if self.STOP:
                    return
            self.logger.info("Hit switch...")
            trigPos = self.readReg(motor | self.LATCHED)
            self.logger.debug("Triggered at %d"%trigPos)
            #Go to trigger position
            self.writeReg(motor | self.TARGET, trigPos)
            while not self.getOnTarget(motor):
                sleep(0.1)
            #set to 0
            self.writeReg(motor | self.ACTUAL, 0)
            self.writeReg(motor | self.TARGET, 0)
            homingError = (0x7fffff - trigPos) - currentPos
            self.logger.info("Homing error: %d"%homingError)
            if motor == self.MOTOR1:
                self.m1Homing = False
                self.m1Homed = True
            elif motor == self.MOTOR2:
                self.m2Homing = False
                self.m2Homed = True
            elif motor == self.MOTOR3:
                self.m3Homing = False
                self.m3Homed = True



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
