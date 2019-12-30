from core import Action
from core import Data

class PublishGeocacheAction(Action):
    def __init__(self, scenefile):
        super(PublishGeocacheAction, self).__init__(scenefile.match)
        if scenefile.graph:
            self.setGraph(scenefile.graph)

