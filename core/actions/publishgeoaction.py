import logging

from core import Action
from core import Data

logger = logging.getLogger(__name__)

class PublishGeoAction(Action):
    def __init__(self, match):
        super(PublishGeoAction, self).__init__(match)

    def knownData(self):
        return ["GeoData"]
