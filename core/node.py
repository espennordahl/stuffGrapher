
class Node:
    """
    Base class for all node types
    """
    def __init__(self, match):
        self.attributes = {}
        self.plugs = []
        self.match = match
        self.graph = None

    def setGraph(self, graph):
        self.graph = graph
        self.graph.addNode(self)
