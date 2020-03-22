import logging

from core import Action
from core import Data

logger = logging.getLogger(__name__)

class PublishGeocacheAction(Action):
    def __init__(self, match):
        super(PublishGeocacheAction, self).__init__(match)

    def knownData(self):
        return ["GeocacheData"]
