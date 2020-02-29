from core import Action
from core import Data

class ComprenderAction(Action):
    def __init__(self, match):
        super(ComprenderAction, self).__init__(match)

    def knownData(self):
        return ["ComprenderData"] 
