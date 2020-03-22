import logging

from core.scenefile import SceneFile
from core.actions import *

logger = logging.getLogger(__name__)

class HoudiniFile(SceneFile):
    def __init__(self, match):
        super(HoudiniFile, self).__init__(match)

        ## Templates
        self.attributes["template"].addElement("FXTemplate")
        self.attributes["template"].addElement("LayoutTemplate")
        self.attributes["template"].value = "FXTemplate"

        ## Default department
        self["department"] = "fx"

    def knownActions(self):
        return [
                "RenderAction",
                "PublishGeoAction", 
                "PublishGeocacheAction",
                "PublishLookdevAction"
                ]
