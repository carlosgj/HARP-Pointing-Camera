import TMC2130
from time import sleep

m1 = TMC2130.TMC2130(0, 0)
m2 = TMC2130.TMC2130(0, 1)

m1.initialize()
m2.initialize()

while True:
    sleep(0.2)