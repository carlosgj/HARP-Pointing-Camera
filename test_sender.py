import CTD
from HDLC import SICHDLC
import serial

ser = serial.Serial('COM13', 115200, timeout=1)
hdlc = SICHDLC(debug=True)

opcodes = {}
for key, val in CTD.__dict__.iteritems():
    if key.startswith("OP_"):
        opcodes[key] = val

for key in opcodes.keys():
    print key

while True:
    try:
        cmd = raw_input("cmd>")
        cmd = cmd.upper()
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