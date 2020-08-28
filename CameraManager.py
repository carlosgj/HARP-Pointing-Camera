try:
    from picamera import PiCamera
except ImportError:
    from mockPicamera import PiCamera
from datetime import datetime
import logging
from os import path

class CameraManager():
    def __init__(self, name="CAMMGR", datadir="."):
        self.logger = logging.getLogger(name)
        self.cam = PiCamera(resolution=(3280, 2464))
        self.datadir = datadir

    def __del__(self):
        self.cam.close()

    def initialize(self):
        pass

    def getAutoParams(self):
        pass

    def autoSetParams(self):
        pass

    def collect(self, name=None, nameSuffix="", bayer=True):
        if name is None:
            name = datetime.now().isoformat()
        if nameSuffix:
            name += ('_' + nameSuffix)
        name += '.jpg'
        self.cam.capture(path.join(self.datadir, name), format='jpg', bayer=bayer)

    def run(self):
        pass