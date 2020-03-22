import logging

from core import Action
from core import Data

logger = logging.getLogger(__name__)

class ComprenderAction(Action):
    def __init__(self, match):
        super(ComprenderAction, self).__init__(match)

    def knownData(self):
        return ["ComprenderData"] 
