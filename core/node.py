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
        self.addAttribute(OutputAttribute("out", self, hidden=True))

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
            logging.error("addAttribute takes only Attribute objects. Got " + str(type(attribute)))
        if attribute.key in self.attributes:
            logging.warning("Attribute with name {nm} already exists. Ignoring.".format(nm=attribute.key))
            return
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

    @classmethod
    def deserialize(cls, root):
        if root["class"] != "Node":
            logging.error("Wrong deserializer called: " + root["class"])
        obj = Node(root["match"])

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
        self.attributes[key] = value
