from core import Action
from core import Data

class PublishGeoAction(Action):
    def __init__(self, scenefile):
        super(PublishGeoAction, self).__init__(scenefile.match)
        if scenefile.graph:
            self.setGraph(scenefile.graph)

