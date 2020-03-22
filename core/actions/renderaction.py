import logging

from core import Action
from core import Data
from core.attributes import *

logger = logging.getLogger(__name__)

class RenderAction(Action):
    def __init__(self, match):
        super(RenderAction, self).__init__(match)

        self.addAttribute(BoolAttribute("updateResources", True))

    def knownData(self):
        return ["RenderData"]
