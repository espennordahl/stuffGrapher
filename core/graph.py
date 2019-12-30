import logging

class Graph:
    def __init__(self):
        self.nodes = []

    def addNode(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
            if node.graph != self:
                node.setGraph(self)
