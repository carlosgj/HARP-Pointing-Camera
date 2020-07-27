import crcmod
import struct

START_FLAG = chr(0xaa)
END_FLAG = chr(0x7e)
ESCAPE = chr(0x7D)

class SICHDLC():
    def __init__(self, debug = False):
        self.debug = debug
        self.crcfn = crcmod.predefined.mkCrcFun('crc-aug-ccitt')
        assert self.crcfn('123456789') == 0xe5cc
        
    class ByteStuffError(Exception):
        pass
        
    class LengthError(Exception):
        pass
        
    class CRCError(Exception):
        pass
        
    class FlagError(Exception):
        pass
        
    def prettyHexPrint(self, data):
        if isinstance(data, basestring):
            return ":".join("{:02x}".format(ord(c)) for c in data)
        else: 
            return ":".join("{:02x}".format(c) for c in data)
        
    def createPacket(self, opcode, data):
        packet = chr(opcode)
        for byte in data:
            packet += chr(byte)
        if self.debug:
            print "Opcode: 0x%02x Data: %s"%(opcode, self.prettyHexPrint(data))
        #Prepend length
        packet = chr(1 + len(data) + 2) + packet #opcode + data + CRC
        if self.debug:
            print "Length: %d bytes"%ord(packet[0])
        
        #Append CRC
        crc = self.crcfn(packet)
        if self.debug:
            print "CRC of %s is 0x%04x."%(self.prettyHexPrint(packet), crc)
        packet += struct.pack('>H', crc)
        
        #Byte-stuffing
        if self.debug:
            print "Pre byte-stuffing: ", self.prettyHexPrint(packet)
        stuffedPacket = ""
        for c in packet:
            if c in [START_FLAG, END_FLAG, ESCAPE]:
                stuffedPacket += ESCAPE
                stuffedPacket += chr(ord(c) ^ 0b00100000)
            else:
                stuffedPacket += c
        packet = stuffedPacket
        if self.debug:
            print "Post byte-stuffing: ", self.prettyHexPrint(packet)
        
        #Add start and end flags
        packet = START_FLAG + packet + END_FLAG
        return packet
            
        
    def parsePacket(self, data):
        if self.debug:
            print "Original packet: %s"%self.prettyHexPrint(data)
        #Validate flags 
        if not (data.startswith(START_FLAG) and data.endswith(END_FLAG)):
            raise self.FlagError
        data = data[1:-1]
        
        #Undo byte stuffing 
        if self.debug:
            print "Packet: %s"%self.prettyHexPrint(data)
        unstuffed = ""
        i = 0
        while i < len(data):
            c = data[i]
            if c == ESCAPE:
                ec = data[i+1]
                uec = chr(ord(ec) ^ 0b00100000)
                if uec in [START_FLAG, END_FLAG, ESCAPE]:
                    unstuffed += uec
                    i += 1
                else:
                    raise self.ByteStuffError
            else:
                unstuffed += c
            i += 1
        data = unstuffed
        if self.debug:
            print "Unstuffed packet: %s"%self.prettyHexPrint(data)
            
        #Validate length
        statedLength = ord(data[0])
        actualLength = len(data)-1 #-1 for the lenght byte itself
        if self.debug:
            print "Packet length should be %d, is %d."%(statedLength, actualLength)
        if statedLength != actualLength:
            raise self.LengthError
            
        #Check CRC
        packet = data[:-2]
        crc = data[-2:]
        statedCRC = struct.unpack('>H', crc)[0]
        computedCRC = self.crcfn(packet)
        if self.debug:
            print "Received CRC: 0x%04x Computed CRC: 0x%04x"%(statedCRC, computedCRC)
        if statedCRC != computedCRC:
            raise self.CRCError
            
        return ord(packet[1]), packet[2:]
        
if __name__ ==  "__main__":
    this = SICHDLC(debug = True)
    packet = this.createPacket(0xaa, [1,2,0x7d,4])
    print this.prettyHexPrint(packet)
    print "-----------------"
    opcode, data = this.parsePacket(packet)
    print "Opcode: 0x%02x Data: %s"%(opcode, this.prettyHexPrint(data))