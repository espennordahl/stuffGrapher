import logging

from .node import Node
from .data import Data
import core.actions
from .attributes import *

departments = [
                "anim",
                "conform",
                "comp",
                "fx",
                "layout",
                "lit",
                "model",
                "rig",
                "shd",
                "txtr"
            ]

class SceneFile(Node):
    def __init__(self, match):
        super(SceneFile, self).__init__(match)
        inputAttr = InputAttribute("input", hidden=True)
        inputAttr.setConnectionCallback(self._checkInputConnection)
        self.addAttribute(inputAttr)
        self.addAttribute(EnumAttribute("department", elements=departments))
        self.addAttribute(StringAttribute("partname", "main"))
        self.addAttribute(EnumAttribute("template"))

    def visualName(self):
        return "{department}_{partname}".format(
                department=self["department"].value, 
                partname=self["partname"].value
                )

    def knownActions(self):
        return []

    def createAction(self, actionname, match):
        if actionname not in self.knownActions():
            logger.error("Tried to create incompatible or unknown action: " + actionname)

        if not actionname in dir(core.actions):
            logger.error("Tried to create non existing action object: " + actionname)

        cls = getattr(core.actions, actionname)
        action = cls(match)

        action["scenefile"] = self

        if self.graph:
            self.graph.addNode(action)

        return action

    @classmethod
    def deserialize(cls, root):
        import core.scenefiles
        classname = root["class"]
        if not classname in dir(core.scenefiles):
            logger.error("Unable to deserialize. Unknown classname: " + classname)

        cls = getattr(core.scenefiles, classname)

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
        return isinstance(connection.value, Data)

