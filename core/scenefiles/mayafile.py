import logging

from core.scenefile import SceneFile

class MayaFile(SceneFile):
    def __init__(self, match):
        super(MayaFile, self).__init__(match)

    def knownActions(self):
        return [
                "RenderAction",
                "PublishGeoAction", 
                "PublishGeocacheAction",
                "PublishLookdevAction"
                ] 
