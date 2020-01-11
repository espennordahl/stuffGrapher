import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import Graph, SceneFile, Action, Data
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
        self.pen.setColor(QColor(200,200,200,255))
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
        self.newLine = None

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

    def createNewLine(self, pos):
        if self.type == 'out':
            rect = self.boundingRect()
            pointA = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointA = self.mapToScene(pointA)
            pointB = self.mapToScene(pos)
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
 
    def updateNewLine(self, pos):
        point = self.mapToScene(pos)
        if self.type == 'out':
            self.newLine.pointB = point
        elif self.type == 'in':
            self.newLine.pointA = point

    def connectToItem(self, item):
        logging.debug("Trying to connect to item")
        if self.type == 'out' and item.type == 'in':
            self.newLine.pointB = item.getCenter()
            self.newLine.source = self
            self.newLine.target = item
            item.parentItem().addInput(self.parentItem())
            item.parentItem().input.inLines.append(self.newLine)
            self.newLine = None
        elif self.type == 'in' and item.type == 'out':
            self.newLine.pointA = item.getCenter()
            self.newLine.source = item
            self.newLine.target = self
            self.parentItem().addInput(item.parentItem())
            item.parentItem().output.outLines.append(self.newLine)
            self.newLine = None

    def removeNewLine(self):
        if self.newLine in self.outLines:
            self.outLines.remove(self.newLine)
        else:
            self.inLines.remove(self.newLine)
        self.scene().removeItem(self.newLine)
        self.newLine = None

    def mousePressEvent(self, event):
        self.createNewLine(event.pos())

    def mouseMoveEvent(self, event):
        if self.newLine:
            self.updateNewLine(event.pos())
        else:
            super(NodeSocket, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        item = self.scene().itemAt(event.scenePos().toPoint(), QTransform())
        if item:
            self.connectToItem(item)
        if self.newLine:
            self.removeNewLine()

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

        textWidth = len(node.name) * 10
        nodeWidth = max(100, min(textWidth, 200))
        self.rect = QRect(0,0,nodeWidth,50)
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
        self.selPen.setWidth(3)
        self.selPen.setColor(QColor(255,255,255,255))

        # Text
        self.font = QFont()
        self.font.setPixelSize(20)

    def initUi(self):
        socketSize = 16
        for attribute in self.node.attributes.values():
            if isinstance(attribute, InputAttribute):
                self.input = NodeSocket(QRect(
                                                -socketSize/2,
                                                self.rect.height()/2-socketSize/2,
                                                socketSize,
                                                socketSize
                                                ), self, 'in')
        self.output = NodeSocket(QRect(
                                        self.rect.width()-socketSize/2,
                                        self.rect.height()/2-socketSize/2,
                                        socketSize,
                                        socketSize), self, 'out')

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
        
        painter.drawRoundedRect(self.rect, 5.0, 5.0)
        
        font = painter.font()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(Qt.black)
        painter.drawText(self.rect.adjusted(0,0,-5,0), Qt.AlignCenter, self.node.name)

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

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.node:
                self.node["pos.x"].value = self.pos().x
                self.node["pos.y"].value = self.pos().y
        return QGraphicsItem.itemChange(self, change, value)

    def createConnections(self):
        for attribute in self.node.attributes.values():
            if isinstance(attribute, InputAttribute):
                if not attribute.value:
                    continue
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

    def getBaseColor(self, hue):
        return QColor.fromHsv(hue,120,100)

    def getTopColor(self, color):
        return color.lighter(150)

class SceneNodeItem(NodeItem):
    def __init__(self, node):
        super(SceneNodeItem, self).__init__(node)
        logging.debug("Creating SceneNodeItem")
       
        gradient = QLinearGradient(0,0,0,self.rect.height())
        baseCol = self.getBaseColor(0)
        gradient.setColorAt(1,baseCol)
        gradient.setColorAt(0,self.getTopColor(baseCol))
        self.brush = QBrush(gradient)
        logging.debug("Created SceneNodeItem")

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('Create on disk')
        listAction = menu.addAction('List versions')
        actionMenu = menu.addMenu("Create Action")
        for action in self.node.knownActions():
            actionMenu.addAction(action)
        selectedAction = menu.exec_(event.screenPos())

class ActionNodeItem(NodeItem):
    def __init__(self, node):
        super(ActionNodeItem, self).__init__(node)
        logging.debug("Creating ActionNodeItem")
       
        gradient = QLinearGradient(0,0,0,self.rect.height())
        baseCol = self.getBaseColor(120)
        gradient.setColorAt(1,baseCol)
        gradient.setColorAt(0,self.getTopColor(baseCol))
        self.brush = QBrush(gradient)
        logging.debug("Created ActionNodeItem")

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('Run in tractor')
        selectedAction = menu.exec_(event.screenPos())


class DataNodeItem(NodeItem):
    def __init__(self, node):
        super(DataNodeItem, self).__init__(node)
        logging.debug("Creating DataNodeItem")
       
        gradient = QLinearGradient(0,0,0,self.rect.height())
        baseCol = self.getBaseColor(240)
        gradient.setColorAt(1,baseCol)
        gradient.setColorAt(0,self.getTopColor(baseCol))
        self.brush = QBrush(gradient)
        logging.debug("Created DataNodeItem")

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('List versions')
        selectedAction = menu.exec_(event.screenPos())


