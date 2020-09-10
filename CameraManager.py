try:
    from picamera import PiCamera
except ImportError:
    from mockPicamera import PiCamera
from datetime import datetime
import logging
from os import path
from time import sleep

class CameraManager():
    class CollectParams():
        def __init__(self, name):
            self.name = name
            self.bayer = False
            self.nameSuffix = False

    def __init__(self, name="CAMMGR", datadir="."):
        self.logger = logging.getLogger(name)
        self.cam = None
        #self.cam = PiCamera(resolution=(3280, 2464))
        self.datadir = datadir
        self.collectFlag = False
        self.params = self.CollectParams("")

    def __del__(self):
        if self.cam:
            self.cam.close()

    def initialize(self):
        self.logger.info("Initializing...")

    def getAutoParams(self):
        pass

    def autoSetParams(self):
        pass

    def doCollect(self, params):
        if params.name is None:
            name = datetime.now().isoformat()
        if params.nameSuffix:
            name += ('_' + params.nameSuffix)
        name += '.png'
        self.cam.capture(path.join(self.datadir, name), format='png', bayer=params.bayer)

    def collect(self, name=None, nameSuffix="", bayer=True):
        self.params.name = name
        self.params.nameSuffix = nameSuffix
        self.params.bayer = bayer
        self.collectFlag = True

    def run(self):
        if self.collectFlag:
            self.doCollect(self.params)
            self.collectFlag = False
        else:
            sleep(0.1)
