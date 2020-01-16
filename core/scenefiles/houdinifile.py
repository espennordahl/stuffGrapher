import logging

from core.scenefile import SceneFile
from core.actions import *

class HoudiniFile(SceneFile):
    def __init__(self, match):
        super(HoudiniFile, self).__init__(match)

        ## Templates
        self.attributes["template"].addElement("FXTemplate")
        self.attributes["template"].addElement("LayoutTemplate")

    def knownActions(self):
        return [
                "RenderAction",
                "PublishGeoAction", 
                "PublishGeocacheAction",
                "PublishLookdevAction"
                ]
