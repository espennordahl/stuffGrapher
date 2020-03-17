import logging

from .node import Node
from core import data
from .attributes import *

class Action(Node):
    def __init__(self, match):
        super(Action, self).__init__(match)
        inputAttr = InputAttribute("scenefile", None, hidden=True)
        inputAttr.setConnectionCallback(self._checkInputConnection)
        self.addAttribute(inputAttr)
        self.addAttribute(StringAttribute("subpart", "default"))

    def visualName(self):
        if self.attributes["scenefile"].value:
            return "{scenefile}_{subpart}".format(
                            scenefile=self.attributes["scenefile"].value.visualName(),
                            subpart=self.attributes["subpart"].value
                            )
        else:
            return self.name

    def knownData(self):
        return []

    @classmethod
    def deserialize(cls, root):
        import core.actions
        classname = root["class"]
        if not classname in dir(core.actions):
            logger.error("Unable to deserialize. Unknown classname: " + classname)

        cls = getattr(core.actions, classname)

        match = root["match"]

        obj = cls(root["match"])

        attributes = root["attributes"]
        for attrname in attributes:
            attribute = Attribute.deserialize(attributes[attrname])
            attribute.parent = obj
            if attrname in obj.attributes:
                obj.attributes[attrname] = attribute
            else:
                obj.addAttribute(attribute)

        return obj

    def _checkInputConnection(self, connection):
        if not isinstance(connection, OutputAttribute):
            logger.debug("Connection not an OutputAttribute")
            return False
        from .scenefile import SceneFile
        return isinstance(connection.parent, SceneFile)

    def createData(self, dataType):
        if dataType not in self.knownData():
            logger.error("Tried to create incompatible or unknown data: " + dataType)

        if not dataType in dir(data):
            logger.error("Tried to create non existing data type: " + dataType)

        cls = getattr(data, dataType)
        node = cls(self.match)

        node["action"] = self

        if self.graph:
            self.graph.addNode(node)

        return node


