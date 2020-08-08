import HDLC
import time
import serial
import CTD
import struct
import psutil
from enum import Enum
import TMC2130
import TMC429
import CommunicationManager

SERIAL_PORT = "COM4"
BAUD = 115200

states = Eunm('State', "IDLE HOMING READY MOVING COLLECTING")

motor1 = TMC2130.TMC2130(0, 0)
motor2 = TMC2130.TMC2130(0, 1)
mc = TMC429.TMC429()

while True:
    #Main loop
    #Check to see if we got any commands
    
    #Service motors
    
    #Service camera
                
                
if __name__ == "__main__":
    this = CommunicationManager()
    this.run()