import logging
import sys

from core import actions
from core import scenefiles
from core import data
from core import Node
from core.attributes import *

logger = logging.getLogger(__name__)

class Graph:
    def __init__(self):
        self.nodes = {}
        self._graphChangedCallbacks = []

    def graphChanged(self):
        for func in self._graphChangedCallbacks:
            if callable(func):
                func()

    def addGraphChangedCallback(self, func):
        if func not in self._graphChangedCallbacks:
            self._graphChangedCallbacks.append(func)

    def clear(self):
        self.nodes.clear()
        self.graphChanged()

    def paste(self, data):
        tempGraph = Graph.deserialize(data)
        for node in tempGraph.nodes.values():
            self.addNode(node)

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
            logger.error("Asked to rename a node not in the graph")
            raise Exception
        self.nodes.pop(node.name)
        newname = self.createUniqueName(newname)
        node._name = newname 
        self.nodes[node.name] = node

    def addNode(self, node):
        name = self.createUniqueName(node.name)
        node._name = name
        self.nodes[node.name] = node
        if node.graph is not self:
            node.setGraph(self)
        logger.info("Added node: {}".format(node.name))
        logger.debug("Node list: {}".format(self.nodes.keys()))
        self.graphChanged()

    def removeNode(self, node):
        for key, value in self.nodes.items():
            if value == node:
                del self.nodes[key]
                self.graphChanged()
                return

    def createNode(self, classname, match):
        module = None
        if classname in dir(scenefiles):
            module = scenefiles
        elif classname in dir(actions):
            module = actions
        elif classname in dir(data):
            module = data

        if not module:
            logger.error("Unable to find Node class: {nm}".format(nm=classname))
            raise Exception

        cls = getattr(module, classname)
        node = cls(match)
        self.addNode(node)
        return node

    def serialize(self):
        root = {}
        root["class"] = "Graph"
        root["nodes"] = []
        for node in self.nodes.values():
            root["nodes"].append(node.serialize())
        return root

    @classmethod
    def deserialize(cls, root):
        classname = root["class"]
        if classname != "Graph":
            logger.error("Wrong serializer called. Expected Graph, got " + classname)
            raise Exception

        graph = Graph()
        for node in root["nodes"]:
            classname = node["class"]
            logger.debug("Deserializing {} object".format(classname))
            module = None
            if classname in dir(scenefiles):
                module = scenefiles
            elif classname in dir(actions):
                module = actions
            elif classname in dir(data):
                module = data
            if not module:
                logger.error("Unable to find Node class: {nm}".format(nm=classname))
                raise Exception

            cls = getattr(module, classname)
            obj = cls.deserialize(node)
            graph.addNode(obj)
        
        ## Connection attributes will deserialize to strings.
        ## So after all nodes are initialized we hook them up
        ## TODO: There's probably a smarter/cleaner way to do this

        for node in graph.nodes.values():
            for attribute in node.attributes.values():
                ## Update: Uhm, now things have truly gotten messy
                ## Will clean this up very soon (famous last words..)
                if isinstance(attribute, InputAttribute):
                    if isinstance(attribute, ArrayInputAttribute):
                        if attribute.value:
                            nodelist = []
                            for nodename in attribute.value:
                                nodelist.append(graph.nodes[nodename])
                            attribute.value = nodelist
                        else:
                            attribute.value = []
                    else:
                        nodename = attribute.value
                        if nodename:
                            attribute.value = graph.nodes[nodename]

        return graph

    def __eq__(self, other):
        return self.nodes == other.nodes

