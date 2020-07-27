from CTD import opcodes
from HDLC import SICHDLC
import serial

ser = serial.Serial('COM7', 115200, timeout=1)
hdlc = SICHDLC(debug=True)

while True:
    try:
        cmd = raw_input("cmd>")
        cmd = cmd.lower()
        if cmd in opcodes:
            oc = opcodes[cmd]
            packet = hdlc.createPacket(oc, [])
            print "Sending %s"%hdlc.prettyHexPrint(packet)
            ser.write(packet)
        else:
            print "Unrecognized command."
    except KeyboardInterrupt:
        break
        
        
ser.close()