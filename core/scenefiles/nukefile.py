import logging

from core.scenefile import SceneFile

class NukeFile(SceneFile):
    def __init__(self, match):
        super(NukeFile, self).__init__(match)

