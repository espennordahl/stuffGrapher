import logging

from .node import Node
from .attributes import *

class Data(Node):
    def __init__(self, match):
        super(Data, self).__init__(match)
        inputAttr = InputAttribute("action", None, hidden=True)
        inputAttr.setConnectionCallback(self._checkInputConnection)
        self.addAttribute(inputAttr)

    def visualName(self):
        if self.attributes["action"].value:
            return self.attributes["action"].value.visualName()
        else:
            return self.name

    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logging.debug("Connection not an OutputAttribute")
            return False
        from .action import Action
        return isinstance(connection.value, Action)

class GeoData(Data):
    def __init__(self, match):
       super(GeoData, self).__init__(match)

    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logging.debug("Connection not an OutputAttribute")
            return False
        from .actions import PublishGeoAction
        return isinstance(connection.parent, PublishGeoAction)


class GeocacheData(Data):
    def __init__(self, match):
       super(GeocacheData, self).__init__(match)


    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logging.debug("Connection not an OutputAttribute")
            return False
        from .actions import PublishGeocacheAction
        return isinstance(connection.parent, PublishGeocacheAction)


class LookdevData(Data):
    def __init__(self, match):
       super(LookdevData, self).__init__(match)

    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logging.debug("Connection not an OutputAttribute")
            return False
        from .actions import PublishLookdevAction
        return isinstance(connection.parent, PublishLookdevAction)

class PlateData(Data):
    def __init__(self, match):
       super(PlateData, self).__init__(match)

    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logging.debug("Connection not an OutputAttribute")
            return False
        from .actions import PublishPlateAction
        return isinstance(connection.parent, PuclishPlateAction)

class RenderData(Data):
    def __init__(self, match):
       super(RenderData, self).__init__(match)

    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logging.debug("Connection not an OutputAttribute")
            return False
        from .actions import RenderAction
        return isinstance(connection.parent, RenderAction)

class ComprenderData(Data):
    def __init__(self, match):
       super(ComprenderData, self).__init__(match)

    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logging.debug("Connection not an OutputAttribute")
            return False
        from .actions import ComprenderAction
        return isinstance(connection.parent, ComprenderAction)


