import logging

from .node import Node
import core.actions

class SceneFile(Node):
    def __init__(self, match):
        super(SceneFile, self).__init__(match)

    def knownActions(self):
        return []

    def createAction(self, actionname, match):
        if actionname not in self.knownActions():
            logging.error("Tried to create incompatible or unknown action: " + actionname)

        if not actionname in dir(core.actions):
            logging.error("Tried to create non existing action object: " + actionname)

        cls = getattr(core.actions, actionname)
        action = cls(match)

        action["scenefile"].value = self

        if self.graph:
            self.graph.addNode(action)

        return action

    @classmethod
    def deserialize(cls, root):
        import core.scenefiles
        classname = root["class"]
        if not classname in dir(core.scenefiles):
            logging.error("Unable to deserialize. Unknown classname: " + classname)

        cls = getattr(core.scenefiles, classname)

        match = root["match"]

        obj = cls(root["match"])

        attributes = root["attributes"]
        for attrname in attributes:
            attribute = Attribute.deserialize(attributes[attrname])
            if attrname in obj.attributes:
                obj[attrname] = attribute
            else:
                obj.addAttribute(attribute)

        return obj

