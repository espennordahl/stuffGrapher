import logging

from .node import Node
from .attributes import *

class Action(Node):
    def __init__(self, match):
        super(Action, self).__init__(match)
        self.addAttribute(InputAttribute("scenefile", None, hidden=True))
        self.addAttribute(StringAttribute("subpart", "default"))

    def visualName(self):
        if self.attributes["scenefile"].value:
            return "{scenefile}_{subpart}".format(
                            scenefile=self.attributes["scenefile"].value.visualName(),
                            subpart=self.attributes["subpart"].value
                            )
        else:
            return self.name

    @classmethod
    def deserialize(cls, root):
        import core.actions
        classname = root["class"]
        if not classname in dir(core.actions):
            logging.error("Unable to deserialize. Unknown classname: " + classname)

        cls = getattr(core.actions, classname)

        match = root["match"]

        obj = cls(root["match"])

        attributes = root["attributes"]
        for attrname in attributes:
            attribute = Attribute.deserialize(attributes[attrname])
            if isinstance(attribute, OutputAttribute):
                attribute.value = obj
            if attrname in obj.attributes:
                obj[attrname] = attribute
            else:
                obj.addAttribute(attribute)

        return obj

