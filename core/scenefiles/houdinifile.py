import logging

from core.scenefile import SceneFile

class HoudiniFile(SceneFile):
    def __init__(self, match):
        super(HoudiniFile, self).__init__(match)

