import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .nodeitem import *

from core import Graph, SceneFile, Action, Data
from core.attributes import *


class NodeGraphView(QGraphicsView):
    def __init__(self, parent=None):
        super(NodeGraphView, self).__init__(parent)
        self.nodes = []
        self.shot = None

        scene = QGraphicsScene()
        scene.setSceneRect(0,0,32000,32000) 
        self.setScene(scene)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def createNode(self, classname):
        if not self.shot:
            logging.warning("No shot selected. Unable to create node")
            return
        
        node = self.shot.graph.createNode(classname, "foo") 

        item = self.itemFromNode(node)

        item.setPos(self.scene().width()/2, self.scene().height()/2)

        self.addNodeItem(item)

    def addNodeItem(self, node):
        scene = self.scene()
        scene.addItem(node)
        self.nodes.append(node)

    def itemFromNode(self, node):
        if isinstance(node, SceneFile):
            return SceneNodeItem(node)
        elif isinstance(node, Action):
            return ActionNodeItem(node)
        elif isinstance(node, Data):
            return DataNodeItem(node)
        else:
            logging.warining("Unable to create graphics item for node type: " + node.__class__.__name__)
            return None
 

    def setShot(self, shot):
        logging.debug("Setting shot: " + shot.name)
        self.shot = shot
        self.scene().clear()

        if not self.shot.graph:
            logging.debug("No graph for shot yet. Creating one")
            self.shot.graph = Graph()
        else:
            graph = self.shot.graph
            logging.debug("Graph has {num} nodes. Populating.".format(num=len(graph.nodes)))
            items = []
            ## Nodes first
            for node in graph.nodes.values():
                item = self.itemFromNode(node)

                items.append(item)
                if node.hasAttribute("pos.x"):
                    x = node["pos.x"].value()
                    y = node["pos.y"].value()
                    item.setPos(x, y)
                self.addNodeItem(item)

            ## Then connections
            for item in items:
                item.createConnections()
