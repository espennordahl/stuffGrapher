import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import Graph
from core.attributes import *

class NodeLine(QGraphicsPathItem):
    def __init__(self, pointA, pointB):
        super(NodeLine, self).__init__()
        self._pointA = pointA
        self._pointB = pointB
        self._source = None
        self._target = None
        self.setZValue(-1)
        self.setBrush(QBrush(Qt.NoBrush))
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(QColor(230,230,230,255))
        self.setPen(self.pen)

    def mousePressEvent(self, event):
        self.pointB = event.pos()

    def mouseMoveEvent(self, event):
        self.pointB = event.pos()

    def updatePath(self):
        path = QPainterPath()
        path.moveTo(self.pointA)
        dx = self.pointB.x() - self.pointA.x()
        dy = self.pointB.y() - self.pointA.y()
        ctrl1 = QPointF(self.pointA.x() + dx * 0.25, self.pointA.y() + dy * 0.1)
        ctrl2 = QPointF(self.pointA.x() + dx * 0.75, self.pointA.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, self.pointB)
        self.setPath(path)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawPath(self.path())

    @property
    def pointA(self):
        return self._pointA

    @pointA.setter
    def pointA(self, point):
        self._pointA = point
        self.updatePath()

    @property
    def pointB(self):
        return self._pointB

    @pointB.setter
    def pointB(self, point):
        self._pointB = point
        self.updatePath()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, widget):
        self._source = widget

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, widget):
        self._target = widget


class NodeSocket(QGraphicsItem):
    def __init__(self, rect, parent, socketType):
        super(NodeSocket, self).__init__(parent)
        self.rect = rect
        self.type = socketType

        # Brush.
        self.brush = QBrush()
        self.brush.setStyle(Qt.SolidPattern)
        self.brush.setColor(QColor(60,60,60,255))

        # Pen.
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QColor(20,20,20,255))

        # Lines.
        self.outLines = []
        self.inLines = []

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        return QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def addConnection(self, item):
        if self.type == 'in':
            logging.debug("adding input connection between {i} and {o}".format(
                                i=self.parentItem().node.name,
                                o=item.node.name))
            
            rect = self.boundingRect()
            pointB = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointB = self.mapToScene(pointB)
            pointA = self.mapToScene(item.output.getCenter())
            
            line = NodeLine(pointA, pointB)
            line.source = item.output
            line.target = self

            self.inLines.append(line)
            item.output.outLines.append(line)
            self.scene().addItem(line)

            line.updatePath()

    def mousePressEvent(self, event):
        if self.type == 'out':
            rect = self.boundingRect()
            pointA = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointA = self.mapToScene(pointA)
            pointB = self.mapToScene(event.pos())
            self.newLine = NodeLine(pointA, pointB)
            self.outLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        elif self.type == 'in':
            rect = self.boundingRect()
            pointA = self.mapToScene(event.pos())
            pointB = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointB = self.mapToScene(pointB)
            self.newLine = NodeLine(pointA, pointB)
            self.inLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        else:
            super(NodeSocket, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.type == 'out':
            pointB = self.mapToScene(event.pos())
            self.newLine.pointB = pointB
        elif self.type == 'in':
            pointA = self.mapToScene(event.pos())
            self.newLine.pointA = pointA
        else:
            super(NodeSocket, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        item = self.scene().itemAt(event.scenePos().toPoint(), QTransform())
        if self.type == 'out' and item.type == 'in':
            self.newLine.source = self
            self.newLine.target = item
            item.parentItem().addInput(self.parentItem())
            item.parentItem().input.inLines.append(self.newLine)
            self.newLine.pointB = item.getCenter()
        elif self.type == 'in' and item.type == 'out':
            self.newLine.source = item
            self.newLine.target = self
            self.parentItem().addInput(item.parentItem())
            item.parentItem().output.outLines.append(self.newLine)
            self.newLine.pointA = item.getCenter()
        else:
            super(NodeSocket, self).mouseReleaseEvent(event)

    def getCenter(self):
        rect = self.boundingRect()
        center = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
        center = self.mapToScene(center)
        return center



class NodeItem(QGraphicsItem):
    def __init__(self, node=None):
        super(NodeItem, self).__init__()
        self.node = node
        if self.node:
            if not self.node.hasAttribute("pos.x"):
                self.node.addAttribute(FloatAttribute("pos.x", self.pos().x))
            if not self.node.hasAttribute("pos.y"):
                self.node.addAttribute(FloatAttribute("pos.y", self.pos().y))

        self.input = None
        self.output = None

        self.rect = QRect(0,0,100,60)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.initUi()

        # Brush.
        self.brush = QBrush()
        self.brush.setStyle(Qt.SolidPattern)
        self.brush.setColor(QColor(100,100,100,255))

        # Pen.
        self.pen = QPen()
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QColor(20,20,20,255))

        self.selPen = QPen()
        self.selPen.setStyle(Qt.SolidLine)
        self.selPen.setWidth(1)
        self.selPen.setColor(QColor(255,255,255,255))

    def initUi(self):
        for attribute in self.node.attributes.values():
            if isinstance(attribute, InputAttribute):
                self.input = NodeSocket(QRect(-10,20,20,20), self, 'in')
        self.output = NodeSocket(QRect(90,20,20,20), self, 'out')

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        return QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        if self.isSelected():
            painter.setPen(self.selPen)
        else:
            painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def mouseMoveEvent(self, event):
        super(NodeItem, self).mouseMoveEvent(event)
        if self.output:
            for line in self.output.outLines:
                line.pointA = line.source.getCenter()
                line.pointB = line.target.getCenter()
        if self.input:
            for line in self.input.inLines:
                line.pointA = line.source.getCenter()
                line.pointB = line.target.getCenter()

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('make')
        makeFromHere = menu.addAction('make from here')
        debugConnections = menu.addAction('debug connections')
        selectedAction = menu.exec_(event.screenPos())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.node:
                self.node["pos.x"].value = self.pos().x
                self.node["pos.y"].value = self.pos().y
        return QGraphicsItem.itemChange(self, change, value)

    def createConnections(self):
        for attribute in self.node.attributes.values():
            if isinstance(attribute, InputAttribute):
                logging.debug("Creating intput connection")
                items = self.scene().items()
                item = None
                for x in items:
                    if isinstance(x, NodeItem):
                        if x.node == attribute.value:
                            item = x
                if not item:
                    logging.error("Couldn't find item by name: " + str(attribute.value.name))
                self.input.addConnection(item)

    def addInput(self, item):
        for attribute in self.node.attributes.values():
            if isinstance(attribute, InputAttribute):
                attribute.value = item.node

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
        self.drag = False

    def createNode(self, classname):
        if not self.shot:
            logging.warning("No shot selected. Unable to create node")
            return
        
        node = self.shot.graph.createNode(classname, "foo") 

        item = NodeItem(node)
        item.setPos(self.scene().width()/2, self.scene().height()/2)

        self.addNodeItem(item)

    def addNodeItem(self, node):
        scene = self.scene()
        scene.addItem(node)
        self.nodes.append(node)

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
                item = NodeItem(node)
                items.append(item)
                if node.hasAttribute("pos.x"):
                    x = node["pos.x"].value()
                    y = node["pos.y"].value()
                    item.setPos(x, y)
                self.addNodeItem(item)

            ## Then connections
            for item in items:
                item.createConnections()
