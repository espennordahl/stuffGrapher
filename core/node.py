import logging

from .attributes import *

class Node:
    """
    Base class for all node types
    """
    def __init__(self, match):
        self.attributes = {}
        self.match = match
        self.graph = None

    def addAttribute(self, attribute):
        if not isinstance(attribute, Attribute):
            logging.error("addAttribute takes only Attribute objects. Got " + type(attribute))
        if attribute.name in self.attributes:
            logging.warning("Attribute with name {nm} already exists. Ignoring.".format(nm=attribute.name))
            return
        self.attributes[attribute.name] = attribute

    def setGraph(self, graph):
        self.graph = graph
        self.graph.addNode(self)
