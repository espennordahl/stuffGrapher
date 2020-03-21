import logging

from .graph import Graph

class Shot:
    def __init__(self, name):
        self.name = name
        self._parent = None
        self.graph = None


    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if value:
            self.graph = value.graph
            self._parent = value
        else:
            self.graph = Graph()
            self._parent = None

    def serialize(self):
        root = {}
        
        root["class"] = "Shot"
        
        root["name"] = self.name
        
        if self.graph:
            root["graph"] = self.graph.serialize()
        else:
            root["graph"] = None
        
        if self.parent:
            root["parent"] = self.parent
        else:
            root["parent"] = None

        return root

    @classmethod
    def deserialize(self, root):
        if root["class"] != "Shot":
            logging.error("Wrong deserializer called: " + root["class"])

        name = root["name"]
        obj = Shot(name)
       
        parent = root["parent"]
        if parent:
            obj.parent = parent

        graph = root["graph"]
        if graph:
            obj.graph = Graph.deserialize(graph)

        return obj

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.graph != other.graph:
            return False
        if self.parent != other.parent:
            return False
        return True

