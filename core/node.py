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

    def setGraph(self, graph):
        self.graph = graph
        if self not in graph.nodes.values():
            self.graph.addNode(self)


    @classmethod
    def deserialize(cls, jsonInput):
        obj = Node(jsonInput["match"])
        attributes = jsonInput["attributes"]
        for attribute in attributes:
            obj.addAttribute(Attribute.deserialize(attributes[attribute]))
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
        if self.attributes != other.attributes:
            return False
        if self.match != other.match:
            return False
        return True
