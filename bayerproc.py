from os import path
import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import as_strided

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

rgb[1::2, 0::2, 1] = data[1::2, 0::2] 
rgb[0::2, 0::2, 2] = data[0::2, 0::2] 
rgb[1::2, 1::2, 0] = data[1::2, 1::2] 
rgb[0::2, 1::2, 1] = data[0::2, 1::2] 

print rgb.shape
h = rgb.shape[0]/2
w = rgb.shape[1]/2
print w, h, rgb.dtype
output = np.zeros((h, w, 3), dtype=rgb.dtype)
print output.shape
for x in range(w):
    for y in range(h):
        g1 = rgb[y*2, x*2+1, 1]
        g2 = rgb[y*2+1, x*2, 1]
        g = (g1+g2)/2
        r = rgb[y*2+1, x*2+1, 0]
        b = rgb[y*2, x*2, 2]
        output[y, x, 0] = r
        output[y, x, 1] = g
        output[y, x, 2] = b

output = (output >> 2).astype(np.uint8)
#plt.imshow(output[:, :, 0], cmap='gray')
print np.amax(output)
plt.imshow(output)
plt.show()