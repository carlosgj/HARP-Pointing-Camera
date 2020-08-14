import HDLC
import time
import serial
import CTD
import struct
import psutil
from enum import Enum

SERIAL_PORT = "COM4"
BAUD = 115200

states = Eunm('State', "IDLE HOMING READY MOVING COLLECTING")

class CommunicationManager():
    def __init__(self):
        self.hdlc = HDLC.SICHDLC(debug=False)
        self.ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0.1)
        self.state = states.IDLE

    def __del__(self):
        self.ser.close()

    def run(self):
        buffer = ""
        receiveInProgress = False
            try:
                c = self.ser.read(1)
                if c:
                    #print "Got 0x%02x"%ord(c)
                    if c == HDLC.START_FLAG:
                        receiveInProgress = True
                        print "Got start flag"
                    if receiveInProgress:
                        buffer += c
                    if c == HDLC.END_FLAG:
                        receiveInProgress = False
                        print "Got end flag"
                        try:
                            opcode, data = self.hdlc.parsePacket(buffer)
                        except self.hdlc.CRCError:
                            buffer = ""
                            resp = self.hdlc.createPacket(CTD.RES_INV, [])
                            self.ser.write(resp)
                            return (None, None)
                        print "Opcode: 0x%02x Data: %s"%(opcode, self.hdlc.prettyHexPrint(data))
                        buffer = ""
                        return (opcode, data)
                
                
if __name__ == "__main__":
    this = CommunicationManager()
    this.run()