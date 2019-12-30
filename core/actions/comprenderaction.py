from core import Action
from core import Data

class ComprenderAction(Action):
    def __init__(self, scenefile):
        super(ComprenderAction, self).__init__(scenefile.match)
        if scenefile.graph:
            self.setGraph(scenefile.graph)

    def createWriteNode(self, name):
        match = self.match + "." + name
        data = Data(match)
        if self.graph:
            self.graph.addNode(data)
        return data

