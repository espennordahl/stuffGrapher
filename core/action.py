import logging

from .node import Node
from .attributes import *

class Action(Node):
    def __init__(self, match):
        super(Action, self).__init__(match)
        self.addAttribute(InputAttribute("scenefile", None))
 
 
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
        for attribute in attributes:
            obj.addAttribute(Attribute.deserialize(attributes[attribute]))

        return obj

