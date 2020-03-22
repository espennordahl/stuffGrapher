import logging

from core import Action
from core import Data

logger = logging.getLogger(__name__)

class PublishLookdevAction(Action):
    def __init__(self, match):
        super(PublishLookdevAction, self).__init__(match)

    def knownData(self):
        return ["LookdevData"]
