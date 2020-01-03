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
            logging.error("addAttribute takes only Attribute objects. Got " + type(attribute))
        if attribute.name in self.attributes:
            logging.warning("Attribute with name {nm} already exists. Ignoring.".format(nm=attribute.name))
            return
        self.attributes[attribute.name] = attribute

    def setGraph(self, graph):
        self.graph = graph
        if self not in graph.nodes.values():
            self.graph.addNode(self)


    @classmethod
    class deserialize(cls, jsonInput):
        obj = Node(jsonInput["match"])
        for attribute in jsonInput["attributes"]:
            obj.addAttribute(Attribute.deserialize(jsonInput[key]))
        return obj

    def json(self):
        root = {}
        root["class"] = "Node"
        root["attributes"] = {}
        root["match"] = self.match
        for attributes in self.attributes:
            root["attributes"][self.attribute.name] = self.attribute.json()

    def __eq__(self, other):
        if self.attributes != other.attributes:
            return False
        if self.match != other.match:
            return False
        return True
