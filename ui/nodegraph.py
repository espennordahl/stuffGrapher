import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .nodeitem import *

from core import Node, Graph, SceneFile, Action, Data
from core.attributes import *

from .commands import *

logger = logging.getLogger(__name__)

class NodeGraphView(QGraphicsView):
    selectionChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super(NodeGraphView, self).__init__(parent)
        self.undoStack = parent.undoStack
        self.nodes = []
        self.shot = None
        self.oldSelection = []
        self.mousePosLocal = QPoint(0,0)
        self.mousePosGlobal = QPoint(0,0)

        scene = QGraphicsScene()
        scene.setSceneRect(0,0,32000,32000) 
        scene.selectionChanged.connect(self._selectionChanged)
        self.setScene(scene)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setFocusPolicy(Qt.StrongFocus)

    def contextMenuEvent(self, event):
        super(QGraphicsView, self).contextMenuEvent(event)
        pos = self.mapToScene(self.mousePosLocal)
        itemUnderPointer = self.scene().itemAt(pos, QTransform())
        if hasattr(itemUnderPointer, "contextMenuEvent"):
            itemUnderPointer.contextMenuEvent(event)
        else:
            self.createNodeMenu(event.globalPos())

    def mouseMoveEvent(self, event):
        self.mousePosGlobal = QPoint(event.globalPos())
        self.mousePosLocal = QPoint(event.x(), event.y())
        return super(NodeGraphView, self).mouseMoveEvent(event)

    def event(self, event):
        if (event.type()==QEvent.KeyPress) and (event.key()==Qt.Key_Tab):
            self.createNodeMenu(self.mousePosGlobal)
            return True
        else:
            return super(NodeGraphView, self).event(event)



    def createNodeMenu(self, pos):
        menu = QMenu()
        self.mainWindow.buildCreateNodeMenu(menu)
        selectedAction = menu.exec_(pos)

    def _selectionChanged(self):
        scene = self.scene()
        selection = scene.selectedItems()
        selectedNodes = []
        for item in selection:
            if hasattr(item, "node"):
                if isinstance(item.node, Node):
                    selectedNodes.append(item.node)

        if selectedNodes != self.oldSelection:
            oldSelectionItems = []
            for item in scene.items():
                if hasattr(item, "node"):
                    if isinstance(item.node, Node):
                        if item.node in self.oldSelection:
                            oldSelectionItems.append(item)
            command = SelectNodesCommand(self, oldSelectionItems, selection)
            self.undoStack.push(command)
            self.oldSelection = selectedNodes
            #self.selectionChanged.emit(selectedNodes)

    def createNode(self, classname):
        if not self.shot:
            logging.warning("No shot selected. Unable to create node")
            return
        
        node = self.shot.graph.createNode(classname, "foo") 
        pos = self.mapToScene(self.mousePosLocal)
        node["pos.x"].value = pos.x()
        node["pos.y"].value = pos.y()

        node.graph.graphChanged()
        

    def addNodeItem(self, node):
        scene = self.scene()
        scene.addItem(node)
        self.nodes.append(node)

    def itemFromNode(self, node):
        if isinstance(node, SceneFile):
            return SceneNodeItem(self, node)
        elif isinstance(node, Action):
            return ActionNodeItem(self, node)
        elif isinstance(node, Data):
            return DataNodeItem(self, node)
        else:
            logging.warning("Unable to create graphics item for node type: " + node.__class__.__name__)
            return None
 

    def setShot(self, shot):
        logger.debug("Setting shot: " + shot.name)
        self.shot = shot
        self.scene().clear()

        if not self.shot.graph:
            logger.debug("No graph for shot yet. Creating one")
            self.shot.graph = Graph()
        self.shot.graph.addGraphChangedCallback(self.graphChanged)
        self.graphChanged()

    def shotname(self):
        if self.shot:
            return self.shot.name
        else:
            return None

    def graphChanged(self):
        graph = self.shot.graph
        logger.debug("Graph has {num} nodes. Populating.".format(num=len(graph.nodes)))
        items = []
        ## Nodes first
        nodesInScene = []
        for item in self.scene().items():
            if hasattr(item, "node"):
                logger.debug("Node already in scene: {}".format(item.node.name))
                if item.node in graph.nodes.values():
                    nodesInScene.append(item.node)
                    items.append(item)
                else:
                    self.scene().removeItem(item)

        for node in graph.nodes.values():
            if node in nodesInScene:
                continue
            logger.debug("Node not in scene. Creating {}".format(node.name))
            item = self.itemFromNode(node)
            items.append(item)
            self.addNodeItem(item)

        ## Then connections
        for item in items:
            item.graphChanged()
    
        self.scene().update()
