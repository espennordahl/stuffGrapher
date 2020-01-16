import logging

from core.scenefile import SceneFile

class MayaFile(SceneFile):
    def __init__(self, match):
        super(MayaFile, self).__init__(match)
        
        ## Templates
        self.attributes["template"].addElement("DefaultTemplate")
        self.attributes["template"].addElement("LayoutTemplate")
        self.attributes["template"].addElement("AnimTemplate")
        self.attributes["template"].addElement("LightingTemplate")

    def knownActions(self):
        return [
                "RenderAction",
                "PublishGeoAction", 
                "PublishGeocacheAction",
                "PublishLookdevAction"
                ] 
