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
logger = logging.getLogger("ROOT")
logging.basicConfig(level=logging.INFO)


states = Enum('State', "IDLE HOMING READY MOVING COLLECTING")

motor1 = TMC2130.TMC2130(0, 1, name="MOTOR1")
motor2 = TMC2130.TMC2130(0, 0, name="MOTOR2")
mc = TMC429.TMC429(0, 2, name="MOTCON")
cm = CommunicationManager.CommunicationManager(port="COM12", baud="115200")
cam = CameraManager.CameraManager(datadir="/mnt/data")

m1Thread = Thread(target=motor1.run)
m2Thread = Thread(target=motor2.run)
mcThread = Thread(target=mc.run)
cmThread = Thread(target=cm.run)
camThread = Thread(target=cam.run)

def executeCommand(opcode, data):
        #Commands
        if opcode == CTD.OP_NOOP:
            logger.info("Got NOOP, sending ACK")
            cm.responseQueue.put((CTD.RES_ACK, []))

        elif opcode == CTD.OP_RST:
            #TODO: figure out how to reset Pi
            pass

        elif opcode == CTD.OP_HOME:
            cm.responseQueue.put((CTD.RES_ACK, []))
            motor1.setPower(True)
            motor2.setPower(True)
            mc.m1Homing = True
            mc.m2Homing = True

        elif opcode == CTD.OP_PT:
            if len(data) != 8:
                logger.error("Received OP_PT with %d bytes of data"%len(data))
                cm.responseQueue.put((CTD.RES_IMP, []))
                return
            cm.responseQueue.put((CTD.RES_ACK, []))
            (x, y) = struct.unpack("ff", data)
            logger.debug("Setting mirror angles to %f, %f"%(x, y))
            mc.setTargetDegrees(mc.MOTOR1, x)
            mc.setTargetDegrees(mc.MOTOR2, y)

        elif opcode == CTD.OP_COL:
            pass

        elif opcode == CTD.OP_TSC:
            pass

        elif opcode == CTD.OP_CTS:
            pass

        elif opcode == CTD.OP_CTX:
            pass

        elif opcode == CTD.OP_IDL:
            logger.info("Transitioning to idle state")
            cm.responseQueue.put((CTD.RES_ACK, []))
            motor1.setPower(False)
            motor2.setPower(False)
            mc.m1Homed = False
            mc.m2Homed = False

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
            x = mc.getActualDegrees(mc.MOTOR1)
            y = mc.getActualDegrees(mc.MOTOR2)
            cm.responseQueue.put( ( CTD.RES_ANG, struct.pack("ff", float(x), float(y)) ) )

        elif opcode == CTD.OP_QNF:
            pass

        elif opcode == CTD.OP_QDF:
            pass

        elif opcode == CTD.OP_QLN:
            pass

        elif opcode == CTD.OP_QUT:
            uptime = int( time.time() - psutil.boot_time() )
            logger.info("Got QUT, sending %d (0x%08x)"%(uptime, uptime))
            cm.responseQueue.put( (CTD.RES_TIM, struct.unpack('BBBB', struct.pack('>L', uptime))) )

        elif opcode == CTD.OP_QTIM:
            ctime = int(time.time())
            logger.info("Got QTIM, sending %d (0x%08x)"%(ctime, ctime))
            cm.responseQueue.put( (CTD.RES_TIM, struct.unpack('BBBB', struct.pack('>L', ctime))) )

        elif opcode == CTD.OP_QTMP:
            pass

        else:
            #invalid opcode 
            logger.error("Got invalid opcode 0x%02x"%opcode)
            cm.responseQueue.put( (CTD.RES_IMP, []) )
            
def initialize():
    cam.initialize()
    motor1.initialize()
    motor2.initialize()
    
    mc.initialize()
    mc.setVMin(mc.MOTOR1, 1)
    mc.setVMax(mc.MOTOR1, 30)
    mc.setAMax(mc.MOTOR1, 20)
    mc.setVMin(mc.MOTOR2, 1)
    mc.setVMax(mc.MOTOR2, 30)
    mc.setAMax(mc.MOTOR2, 20)

def run():
    try:
        loopcount = 0
        
        logger.critical("Starting communications manager")
        cmThread.start()

        logger.critical("Starting camera")
        camThread.start()
        
        logger.critical("Starting motor controller")
        mcThread.start()
        
        logger.critical("Starting motor driver 1")
        m1Thread.start()
        
        logger.critical("Starting motor driver 2")
        m2Thread.start()
        while True:
            #Main loop
            if loopcount % 10 == 0:
                logger.debug("Loop %d"%loopcount)
            #Check to see if we got any commands
            if not cm.commandQueue.empty():
                (opcode, data) = cm.commandQueue.get()
                executeCommand(opcode, data)
            else:
                time.sleep(0.1)
                    
            loopcount += 1
    except:
        motor1.STOP = True
        motor2.STOP = True
        mc.STOP = True
        cm.STOP = True
        time.sleep(0.5)
        raise
                
if __name__ == "__main__":
    initialize()
    run()