from core import Action
from core import Data

class RenderAction(Action):
    def __init__(self, scenefile):
        super(RenderAction, self).__init__(scenefile.match)
        if scenefile.graph:
            self.setGraph(scenefile.graph)

    def createRenderLayer(self, name):
        match = self.match + "." + name
        data = Data(match)
        if self.graph:
            self.graph.addNode(data)
        return data

