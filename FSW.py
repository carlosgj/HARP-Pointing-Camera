import HDLC
import time
import CTD
import struct
import psutil
from enum import Enum
import TMC2130
import TMC429
import CommunicationManager
from threading import Thread
import logging
logger = logging.getLogger("ROOT")
logging.basicConfig(level=logging.DEBUG)


states = Enum('State', "IDLE HOMING READY MOVING COLLECTING")

motor1 = TMC2130.TMC2130(0, 0, name="MOTOR1")
motor2 = TMC2130.TMC2130(0, 1, name="MOTOR2")
mc = TMC429.TMC429(0, 2, name="MOTCON")
cm = CommunicationManager.CommunicationManager()

m1Thread = Thread(target=motor1.run)
m2Thread = Thread(target=motor2.run)
mcThread = Thread(target=mc.run)
cmThread = Thread(target=cm.run)

def executeCommand(opcode, date):
        #Commands
        if opcode == CTD.OP_NOOP:
            logger.info("Got NOOP, sending ACK")
            cm.responseQueue.put((CTD.RES_ACK, []))
        elif opcode == CTD.OP_RST:
            #TODO: figure out how to reset 
            pass
        elif opcode == CTD.OP_HOME:
            pass
        elif opcode == CTD.OP_PT:
            pass
        elif opcode == CTD.OP_COL:
            pass
        elif opcode == CTD.OP_TSC:
            pass
        elif opcode == CTD.OP_CTS:
            pass
        elif opcode == CTD.OP_CTX:
            pass
        elif opcode == CTD.OP_IDL:
            pass
        elif opcode == CTD.OP_DFC:
            pass
        elif opcode == CTD.OP_FFC:
            pass
        elif opcode == CTD.OP_STP:
            pass
        elif opcode == CTD.OP_WIE:
            pass
        elif opcode == CTD.OP_WID:
            pass
        elif opcode == CTD.OP_CRS:
            pass
        
        #Queries
        elif opcode == CTD.OP_QSTA:
            pass
        elif opcode == CTD.OP_QANG:
            pass
        elif opcode == CTD.OP_QNF:
            pass
        elif opcode == CTD.OP_QDF:
            pass
        elif opcode == CTD.OP_QLN:
            pass
        elif opcode == CTD.OP_QUT:
            uptime = int( time.time() - psutil.boot_time() )
            print "Got QUT, sending %d (0x%08x)"%(uptime, uptime)
            resp = self.hdlc.createPacket(CTD.RES_TIM, struct.unpack('BBBB', struct.pack('>L', uptime)))
            self.ser.write(resp)
        elif opcode == CTD.OP_QTIM:
            ctime = int(time.time())
            print "Got QTIM, sending %d (0x%08x)"%(ctime, ctime)
            resp = self.hdlc.createPacket(CTD.RES_TIM, struct.unpack('BBBB', struct.pack('>L', ctime)))
            self.ser.write(resp)
        elif opcode == CTD.OP_QTMP:
            pass

        else:
            #invalid opcode 
            resp = self.hdlc.createPacket(CTD.RES_IMP, [])
            self.ser.write(resp)
            
def initialize():
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