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

# print rgb.shape
# h = rgb.shape[0]/2
# w = rgb.shape[1]/2
# print w, h, rgb.dtype
# output = np.zeros((h, w, 3), dtype=rgb.dtype)
# print output.shape
# for x in range(w):
#     for y in range(h):
#         g1 = rgb[y*2, x*2+1, 1]
#         g2 = rgb[y*2+1, x*2, 1]
#         g = (g1+g2)/2
#         r = rgb[y*2+1, x*2+1, 0]
#         b = rgb[y*2, x*2, 2]
#         output[y, x, 0] = r
#         output[y, x, 1] = g
#         output[y, x, 2] = b

# At this point we now have the raw Bayer data with the correct values
# and colors but the data still requires de-mosaicing and
# post-processing. If you wish to do this yourself, end the script here!
#
# Below we present a fairly naive de-mosaic method that simply
# calculates the weighted average of a pixel based on the pixels
# surrounding it. The weighting is provided by a byte representation of
# the Bayer filter which we construct first:

bayer = np.zeros(rgb.shape, dtype=np.uint8)
bayer[1::2, 0::2, 1] = 1
bayer[0::2, 0::2, 2] = 1
bayer[1::2, 1::2, 0] = 1
bayer[0::2, 1::2, 1] = 1

# Allocate an array to hold our output with the same shape as the input
# data. After this we define the size of window that will be used to
# calculate each weighted average (3x3). Then we pad out the rgb and
# bayer arrays, adding blank pixels at their edges to compensate for the
# size of the window when calculating averages for edge pixels.

output = np.empty(rgb.shape, dtype=rgb.dtype)
window = (3, 3)
borders = (window[0] - 1, window[1] - 1)
border = (borders[0] // 2, borders[1] // 2)

rgb = np.pad(rgb, [
    (border[0], border[0]),
    (border[1], border[1]),
    (0, 0),
    ], 'constant')
bayer = np.pad(bayer, [
    (border[0], border[0]),
    (border[1], border[1]),
    (0, 0),
    ], 'constant')

# For each plane in the RGB data, we use a nifty numpy trick
# (as_strided) to construct a view over the plane of 3x3 matrices. We do
# the same for the bayer array, then use Einstein summation on each
# (np.sum is simpler, but copies the data so it's slower), and divide
# the results to get our weighted average:

for plane in range(3):
    p = rgb[..., plane]
    b = bayer[..., plane]
    pview = as_strided(p, shape=(
        p.shape[0] - borders[0],
        p.shape[1] - borders[1]) + window, strides=p.strides * 2)
    bview = as_strided(b, shape=(
        b.shape[0] - borders[0],
        b.shape[1] - borders[1]) + window, strides=b.strides * 2)
    psum = np.einsum('ijkl->ij', pview)
    bsum = np.einsum('ijkl->ij', bview)
    output[..., plane] = psum // bsum

output = (output >> 2).astype(np.uint8)
#plt.imshow(output[:, :, 0], cmap='gray')
print np.amax(output)
plt.imshow(output)
plt.show()