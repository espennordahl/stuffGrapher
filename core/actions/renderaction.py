from core import Action
from core import Data
from core.attributes import *

class RenderAction(Action):
    def __init__(self, scenefile):
        super(RenderAction, self).__init__(scenefile.match)
            ## TODO: Should we do this in superclass..?
        if scenefile.graph:
            self.setGraph(scenefile.graph)

        self.addAttribute(InputAttribute("scenefile", scenefile))
        self.addAttribute(BoolAttribute("updateResources", True))


    def createRenderLayer(self, name):
        match = self.match + "." + name
        data = Data(match)
        data.name = "RenderLayer"
        if self.graph:
            self.graph.addNode(data)
        return data

