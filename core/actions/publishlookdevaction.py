from core import Action
from core import Data

class PublishLookdevAction(Action):
    def __init__(self, scenefile):
        super(PublishLookdevAction, self).__init__(scenefile.match)
        if scenefile.graph:
            self.setGraph(scenefile.graph)


