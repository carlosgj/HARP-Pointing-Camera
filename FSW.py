import HDLC
import time
import CTD
import struct
import psutil
from enum import Enum
import TMC2130
import TMC429
import CommunicationManager
import CameraManager
from threading import Thread
import logging
logging.basicConfig(level=logging.DEBUG)

class PCExecutive():
    states = Enum('State', "IDLE HOMING READY MOVING COLLECTING")
    
    def __init__(self):
        self.logger = logging.getLogger("ROOT")
        self.state = self.states.IDLE
        self.motor1 = TMC2130.TMC2130(0, 1, name="MOTOR1")
        self.motor2 = TMC2130.TMC2130(0, 0, name="MOTOR2")
        self.mc = TMC429.TMC429(0, 2, name="MOTCON")
        self.cm = CommunicationManager.CommunicationManager(port="/dev/pts/2", baud="115200")
        self.cam = CameraManager.CameraManager(datadir="/mnt/data")

        self.m1Thread = Thread(target=self.motor1.run)
        self.m2Thread = Thread(target=self.motor2.run)
        self.mcThread = Thread(target=self.mc.run)
        self.cmThread = Thread(target=self.cm.run)
        self.camThread = Thread(target=self.cam.run)

    def executeCommand(self, opcode, data):
        #Commands
        if opcode == CTD.OP_NOOP:
            self.logger.info("Got NOOP, sending ACK")
            self.cm.responseQueue.put((CTD.RES_ACK, []))

        elif opcode == CTD.OP_RST:
            #TODO: figure out how to reset Pi
            pass

        elif opcode == CTD.OP_HOME:
            self.cm.responseQueue.put((CTD.RES_ACK, []))
            self.mc.setEnable(True)
            self.mc.m1Homing = True
            self.mc.m2Homing = True

        elif opcode == CTD.OP_PT:
            if len(data) != 8:
                self.logger.error("Received OP_PT with %d bytes of data"%len(data))
                self.cm.responseQueue.put((CTD.RES_IMP, []))
                return
            self.cm.responseQueue.put((CTD.RES_ACK, []))
            (x, y) = struct.unpack("ff", data)
            self.logger.debug("Setting mirror angles to %f, %f"%(x, y))
            self.mc.setTargetDegrees(self.mc.MOTOR1, x)
            self.mc.setTargetDegrees(self.mc.MOTOR2, y)

        elif opcode == CTD.OP_COL:
            self.cm.responseQueue.put((CTD.RES_ACK, []))
            self.cam.collect()

        elif opcode == CTD.OP_TSC:
            pass

        elif opcode == CTD.OP_CTS:
            pass

        elif opcode == CTD.OP_CTX:
            pass

        elif opcode == CTD.OP_IDL:
            self.logger.info("Transitioning to idle state")
            self.cm.responseQueue.put((CTD.RES_ACK, []))
            self.mc.setEnable(False)
            self.mc.m1Homed = False
            self.mc.m2Homed = False

        elif opcode == CTD.OP_STP:
            pass

        elif opcode == CTD.OP_WIE:
            pass

        elif opcode == CTD.OP_WID:
            pass

        elif opcode == CTD.OP_CRS:
            pass

        elif opcode == CTD.OP_SCI:
            pass

        elif opcode == CTD.OP_SCG:
            pass

        elif opcode == CTD.OP_SCM:
            pass

        elif opcode == CTD.OP_SCS:
            pass

        elif opcode == CTD.OP_SCW:
            pass
        
        elif opcode == CTD.OP_SCF:
            pass

        elif opcode == CTD.OP_KCS:
            pass

        elif opcode == CTD.OP_KCX:
            pass
        
        #Queries
        elif opcode == CTD.OP_QSTA:
            pass

        elif opcode == CTD.OP_QANG:
            x = self.mc.getActualDegrees(self.mc.MOTOR1)
            y = self.mc.getActualDegrees(self.mc.MOTOR2)
            self.cm.responseQueue.put( ( CTD.RES_ANG, struct.pack("ff", float(x), float(y)) ) )

        elif opcode == CTD.OP_QNF:
            pass

        elif opcode == CTD.OP_QDF:
            pass

        elif opcode == CTD.OP_QLN:
            pass

        elif opcode == CTD.OP_QUT:
            uptime = int( time.time() - psutil.boot_time() )
            self.logger.info("Got QUT, sending %d (0x%08x)"%(uptime, uptime))
            self.cm.responseQueue.put( (CTD.RES_UPT, struct.unpack('BBBB', struct.pack('>L', uptime))) )

        elif opcode == CTD.OP_QTIM:
            ctime = int(time.time())
            self.logger.info("Got QTIM, sending %d (0x%08x)"%(ctime, ctime))
            self.cm.responseQueue.put( (CTD.RES_TIM, struct.unpack('BBBB', struct.pack('>L', ctime))) )

        elif opcode == CTD.OP_QTMP:
            pass

        else:
            #invalid opcode 
            self.logger.error("Got invalid opcode 0x%02x"%opcode)
            self.cm.responseQueue.put( (CTD.RES_IMP, []) )
                
    def initialize(self):
        self.cam.initialize()
        self.motor1.initialize()
        self.motor2.initialize()
        
        self.mc.initialize()
        self.mc.setVMin(self.mc.MOTOR1, 1)
        self.mc.setVMax(self.mc.MOTOR1, 30)
        self.mc.setAMax(self.mc.MOTOR1, 20)
        self.mc.setVMin(self.mc.MOTOR2, 1)
        self.mc.setVMax(self.mc.MOTOR2, 30)
        self.mc.setAMax(self.mc.MOTOR2, 20)

    def run(self):
        try:
            loopcount = 0
            
            self.logger.critical("Starting communications manager")
            self.cmThread.start()

            self.logger.critical("Starting camera")
            self.camThread.start()
            
            self.logger.critical("Starting motor controller")
            self.mcThread.start()
            
            self.logger.critical("Starting motor driver 1")
            self.m1Thread.start()
            
            self.logger.critical("Starting motor driver 2")
            self.m2Thread.start()

            self.mc.m1Homing = True
            self.mc.m2Homing = True
            while True:
                #Main loop
                if loopcount % 10 == 0:
                    self.logger.debug("Loop %d"%loopcount)
                
                self.mc.setTargetStepsCalibrated(self.mc.MOTOR1, 0)
                self.mc.setTargetStepsCalibrated(self.mc.MOTOR2, 0)
                
                #Update state
                newState = self.states.IDLE
                if self.mc.m1Homing or self.mc.m2Homing:
                    newState = self.states.HOMING
                if self.mc.m1Homed and self.mc.m2Homed:
                    if (not self.mc.m1OnTarget) or (not self.mc.m2OnTarget):
                        newState = self.states.MOVING
                    else:
                        newState = self.states.READY
                if self.cam.collectFlag:
                    newState = self.states.COLLECTING
                self.state = newState

                #Check to see if we got any commands
                if not self.cm.commandQueue.empty():
                    (opcode, data) = self.cm.commandQueue.get()
                    self.executeCommand(opcode, data)
                else:
                    time.sleep(0.1)
                        
                loopcount += 1
        except:
            self.mc.setEnable(False)
            self.motor1.STOP = True
            self.motor2.STOP = True
            self.mc.STOP = True
            self.cm.STOP = True
            time.sleep(0.5)
            raise
                
if __name__ == "__main__":
    executive = PCExecutive()
    executive.initialize()
    executive.run()
