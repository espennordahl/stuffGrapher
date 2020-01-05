import logging

from core.scenefile import SceneFile
from core.actions import *

class HoudiniFile(SceneFile):
    def __init__(self, match):
        super(HoudiniFile, self).__init__(match)

    def knownActions(self):
        return [
                "RenderAction",
                "PublishGeoAction", 
                "PublishGeocacheAction",
                "PublishLookdevAction"
                ]
