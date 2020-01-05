from core import Action
from core import Data
from core.attributes import *

class RenderAction(Action):
    def __init__(self, match):
        super(RenderAction, self).__init__(match)

        self.addAttribute(BoolAttribute("updateResources", True))


    def createRenderLayer(self, name):
        match = self.match + "." + name
        data = Data(match)
        data.name = "RenderLayer"
        if self.graph:
            self.graph.addNode(data)
        return data

