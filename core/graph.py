import logging
import sys

from core import actions
from core import scenefiles
from core import data

class Graph:
    def __init__(self):
        self.nodes = {}

    def createUniqueName(self, name):
        """
        Gives the node a name that is unique to the graph
        We make node names unique in the same way as Maya/Nuke/Houidini etc,
        by incrementing a number at the end of the name
        """
        ## If the name is already unique, we're good
        if name not in self.nodes:
            return name

        ## It's not unique, so we increment a number at the end until it's unique
        ## First we have to check if it already ends with a number,
        ## so that "name22" increments to "name23" and not "name221"
        basename = name
        number = 1
        for i in range(0, len(name)):
            tail = name[len(name)-(i+1):]
            if tail.isnumeric():
                number = int(tail)
                basename = name[:len(name)-(i+1)]
            else:
                break
        newname = basename + str(number)
        while(newname in self.nodes):
            number += 1
            newname = basename + str(number)
        return newname

    def renameNode(self, node, newname):
        if node not in self.nodes.values():
            logging.error("Asked to rename a node not in the graph")
        self.nodes.pop(node.name)
        newname = self.createUniqueName(newname)
        node._name = newname 
        self.nodes[node.name] = node

    def addNode(self, node):
        name = self.createUniqueName(node.name)
        node._name = name
        self.nodes[node.name] = node
        if node.graph != self:
            node.setGraph(self)

    def createNode(self, classname, match):
        module = None
        if classname in dir(scenefiles):
            module = scenefiles
        elif classname in dir(actions):
            module = actions
        elif classname in dir(data):
            module = data

        if not module:
            logging.error("Unable to find Node class: {nm}".format(nm=classname))

        cls = getattr(module, classname)
        node = cls(match)
        self.addNode(node)
        return node


