import logging

from core.scenefile import SceneFile

logger = logging.getLogger(__name__)

class MayaFile(SceneFile):
    def __init__(self, match):
        super(MayaFile, self).__init__(match)
        
        ## Templates
        self.attributes["template"].addElement("DefaultTemplate")
        self.attributes["template"].addElement("LayoutTemplate")
        self.attributes["template"].addElement("AnimTemplate")
        self.attributes["template"].addElement("LightingTemplate")

        # Default department
        self["department"] = "lit"

    def knownActions(self):
        return [
                "RenderAction",
                "PublishGeoAction", 
                "PublishGeocacheAction",
                "PublishLookdevAction"
                ] 
