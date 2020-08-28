from os import path
import numpy as np
from matplotlib import pyplot as plt

filename = "PiCamV2-Raw-Chart2.jpg"


size = path.getsize(filename)
bayerLen = 10270208
print "Size: %d bytes"%size
with open(filename, 'rb') as fob:
    fob.seek(size-bayerLen)
    bayer = fob.read()
print "Bayer data length: %d"%len(bayer)
assert bayer[:4] == "BRCM"
header = bayer[:32768]
bayer = bayer[32768:]
data = np.fromstring(bayer, dtype=np.uint8)

data = data.reshape((2480, 4128))[:2464, :4100]

data = data.astype(np.uint16) << 2
for byte in range(4):
    data[:, byte::5] |= ((data[:, 4::5] >> (byte * 2)) & 0b11)
data = np.delete(data, np.s_[4::5], 1)

rgb = np.zeros(data.shape + (3,), dtype=data.dtype)
rgb[1::2, 0::2, 0] = data[1::2, 0::2] # Red
rgb[0::2, 0::2, 1] = data[0::2, 0::2] # Green
rgb[1::2, 1::2, 1] = data[1::2, 1::2] # Green
rgb[0::2, 1::2, 2] = data[0::2, 1::2] # Blue

plt.imshow(rgb)
plt.show()