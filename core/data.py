import logging

from .node import Node
from .attributes import *

class Data(Node):
    def __init__(self, match):
        super(Data, self).__init__(match)
        self.addAttribute(InputAttribute("action", None,hidden=True))

    def visualName(self):
        if self.attributes["action"].value:
            return self.attributes["action"].value.visualName()
        else:
            return self.name


class GeoData(Data):
    def __init__(self, match):
       super(GeoData, self).__init__(match)

class GeocacheData(Data):
    def __init__(self, match):
       super(GeocacheData, self).__init__(match)

class LookdevData(Data):
    def __init__(self, match):
       super(LookdevData, self).__init__(match)

class RenderData(Data):
    def __init__(self, match):
       super(RenderData, self).__init__(match)

class ComprenderData(Data):
    def __init__(self, match):
       super(ComprenderData, self).__init__(match)

