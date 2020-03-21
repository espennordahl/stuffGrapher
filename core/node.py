import logging
import json

from .attributes import *

class Node:
    """
    Base class for all node types
    """
    def __init__(self, match):
        self.attributes = {}
        self.match = match
        self.graph = None
        self._name = self.__class__.__name__
        self.addAttribute(OutputAttribute("out", None, hidden=True))
        self.addAttribute(FloatAttribute("pos.x", 0, hidden=True))
        self.addAttribute(FloatAttribute("pos.y", 0, hidden=True))


    def visualName(self):
        return self.name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self.graph:
            self.graph.renameNode(self, value)
        else:
            self._name = value

    def addAttribute(self, attribute):
        if not isinstance(attribute, Attribute):
            logger.error("addAttribute takes only Attribute objects. Got " + str(type(attribute)))
        if attribute.key in self.attributes:
            logger.warning("Attribute with name {nm} already exists. Ignoring.".format(nm=attribute.key))
            return
        attribute.parent = self
        self.attributes[attribute.key] = attribute

    def hasAttribute(self, attributename):
        return attributename in self.attributes

    def setGraph(self, graph):
        self.graph = graph
        if self not in graph.nodes.values():
            self.graph.addNode(self)

    def inputs(self):
        attrs = []
        for attribute in self.attributes.values():
            if isinstance(attribute, InputAttribute):
                attrs.append(attribute)
        return attrs

    def outputs(self):
        attrs = []
        for attribute in self.attributes.values():
            if isinstance(attribute, OutputAttribute):
                attrs.append(attribute)
        return attrs

    def isUpstream(self, node):
        if node == self:
            return True
        for connection in self.inputs():
            if connection.isUpstream(node):
                return True
        return False

    @classmethod
    def deserialize(cls, root):
        if root["class"] != "Node":
            logger.error("Wrong deserializer called: " + root["class"])
        obj = Node(root["match"])

        attributes = root["attributes"]
        for attrname in attributes:
            attribute = Attribute.deserialize(attributes[attrname])
            attribute.parent = obj
            if attrname in obj.attributes:
                obj.attributes[attrname] = attribute
            else:
                obj.addAttribute(attribute)

        return obj

    def serialize(self):
        root = {}
        root["class"] = self.__class__.__name__
        root["attributes"] = {}
        root["match"] = self.match
        for key, value in self.attributes.items():
            root["attributes"][key] = value.serialize()
        return root

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.attributes != other.attributes:
            return False
        if self.match != other.match:
            return False
        return True

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key].value = value
