import logging
import sys

from core import actions
from core import scenefiles

class Graph:
    def __init__(self):
        self.nodes = {}

    def makeNodeNameUnique(self, node):
        name = node.name
        basename = name
        number = 0
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
        node.name = newname

    def addNode(self, node):
        if node not in self.nodes.values():
            self.makeNodeNameUnique(node)
            self.nodes[node.name] = node
            if node.graph != self:
                node.setGraph(self)

    def createSceneFile(self, classname, match):
        if not classname in dir(scenefiles):
            logging.error("Scene File class doesn't exist: {nm}".format(classname))
            return

        cls = getattr(scenefiles, classname)
        node = cls(match)
        self.addNode(node)
        return node

    def createAction(self, classname, scenefile):
        if not classname in dir(actions):
            logging.error("Action class doesn't exist: {nm}".format(classname))
            return

        cls = getattr(actions, classname)
        node = cls(scenefile)
        self.addNode(node)
        return node

