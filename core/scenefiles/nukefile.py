import logging

from core.scenefile import SceneFile

class NukeFile(SceneFile):
    def __init__(self, match):
        super(NukeFile, self).__init__(match)

        ## Templates
        self.attributes["template"].addElement("CompTemplate")
        self.attributes["template"].addElement("MatchMoveTemplate")
        self.attributes["template"].addElement("SlapcompTemplate")
        self.attributes["template"].addElement("VersionZeroTemplate")
        self.attributes["template"].value = "CompTemplate"

        ## Default department
        self.attributes["department"].value = "comp"


        ## Default partname
        self.attributes["partname"].value = "master"

    def knownActions(self):
        return [
                "ComprenderAction"
                ]
