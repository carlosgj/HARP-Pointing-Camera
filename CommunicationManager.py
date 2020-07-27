import HDLC
import time
import serial
import CTD
import struct
import psutil

SERIAL_PORT = "COM4"
BAUD = 115200

class CommunicationManager():
    def __init__(self):
        self.hdlc = HDLC.SICHDLC(debug=False)
        self.ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

    def __del__(self):
        self.ser.close()

    def run(self):
        buffer = ""
        receiveInProgress = False
        while True:
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
                            continue
                        print "Opcode: 0x%02x Data: %s"%(opcode, self.hdlc.prettyHexPrint(data))
                        buffer = ""
                        if opcode == CTD.OP_NOOP:
                            print "Got NOOP, sending ACK"
                            resp = self.hdlc.createPacket(CTD.RES_ACK, [])
                            self.ser.write(resp)
                        elif opcode == CTD.OP_QTIM:
                            ctime = int(time.time())
                            print "Got QTIM, sending %d (0x%08x)"%(ctime, ctime)
                            resp = self.hdlc.createPacket(CTD.RES_TIM, struct.unpack('BBBB', struct.pack('>L', ctime)))
                            self.ser.write(resp)
                        elif opcode == CTD.OP_QUT:
                            uptime = int( time.time() - psutil.boot_time() )
                            print "Got QUT, sending %d (0x%08x)"%(uptime, uptime)
                            resp = self.hdlc.createPacket(CTD.RES_TIM, struct.unpack('BBBB', struct.pack('>L', uptime)))
                            self.ser.write(resp)
            except KeyboardInterrupt:
                break
                
                
if __name__ == "__main__":
    this = CommunicationManager()
    this.run()