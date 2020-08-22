import HDLC
import time
import serial
import CTD
import struct
import psutil
from enum import Enum
import Queue
import logging

SERIAL_PORT = "COM12"
BAUD = 115200

class CommunicationManager():
    def __init__(self, name="COMMMGR"):
        self.hdlc = HDLC.SICHDLC(debug=False)
        self.ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0.1)
        self.commandQueue = Queue.Queue(10)
        self.responseQueue = Queue.Queue(10)
        self.STOP = False
        self.logger = logging.getLogger(name)

    def __del__(self):
        self.ser.close()

    def run(self):
        buffer = ""
        receiveInProgress = False
        while(True):
            if self.STOP:
                self.logger.critical("Received STOP signal")
                self.ser.close()
                break
            if not self.responseQueue.empty():
                (opcode, data) = self.responseQueue.get()
                self.logger.info("Sending response 0x%0.2x with [%s]"%(opcode, ' '.join(["0x%0.2x"%x for x in data])))
                resp = self.hdlc.createPacket(opcode, data)
                self.ser.write(resp)
            c = self.ser.read(1)
            if c:
                #print "Got 0x%02x"%ord(c)
                if c == HDLC.START_FLAG:
                    receiveInProgress = True
                    self.logger.debug("Got start flag")
                if receiveInProgress:
                    buffer += c
                if c == HDLC.END_FLAG:
                    receiveInProgress = False
                    self.logger.debug("Got end flag")
                    try:
                        opcode, data = self.hdlc.parsePacket(buffer)
                    except self.hdlc.CRCError:
                        buffer = ""
                        resp = self.hdlc.createPacket(CTD.RES_INV, [])
                        self.ser.write(resp)
                    self.logger.info("Opcode: 0x%02x Data: %s"%(opcode, self.hdlc.prettyHexPrint(data)))
                    buffer = ""
                    if not self.commandQueue.full():
                        self.commandQueue.put((opcode, data))
            else:
                time.sleep(0.1)
                
                
if __name__ == "__main__":
    this = CommunicationManager()
    this.run()