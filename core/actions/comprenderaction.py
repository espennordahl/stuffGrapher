from core import Action
from core import Data

class ComprenderAction(Action):
    def __init__(self, match):
        super(ComprenderAction, self).__init__(match)

    def createWriteNode(self, name):
        match = self.match + "." + name
        data = Data(match)
        if self.graph:
            self.graph.addNode(data)
        return data

