import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import Graph, SceneFile, Action, Data
from core.attributes import *

logger = logging.getLogger(__name__)

class NodeLine(QGraphicsPathItem):
    """
    Noodle between two nodes.
    """
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
        """
        Recomputes path. Called after points are changed, or nodes have moved.
        """
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
        if self._source:
            self._source.outLines.remove(self)
        self._source = widget

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, widget):
        if self._target:
            self._target.inLines.remove(self)
        self._target = widget


class NodeSocket(QGraphicsItem):
    """
    Connection point to or out from a node. 
    Each socket refers to either an InputAttribute or an OutputAttribute. 
    Outputs can have any number of outgoing connections, but only Array Inputs
    can have multiple incoming connections.
    """
    def __init__(self, rect, parent, attribute):
        super(NodeSocket, self).__init__(parent)
        self.parent = parent
        self.rect = rect
        self.attribute = attribute

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

    def createNewLine(self, pos=QPointF(0,0)):
        """
        Creates a new line that isn't connected to anything yet.
        This happens when a user drags a noodle out from a Socket,
        and have not yet assigned it to another socket.
        """
        if isinstance(self.attribute, OutputAttribute):
            rect = self.boundingRect()
            pointA = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointA = self.mapToScene(pointA)
            pointB = self.mapToScene(pos)
            self.newLine = NodeLine(pointA, pointB)
            self.outLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        elif isinstance(self.attribute, InputAttribute):
            rect = self.boundingRect()
            pointA = self.mapToScene(pos)
            pointB = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointB = self.mapToScene(pointB)
            self.newLine = NodeLine(pointA, pointB)
            self.inLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        else:
            logger.error("Unable to create new line. Attribute is not input or output")
 
    def updateNewLine(self, pos):
        """
        Updates the positions for the newline.
        Called mostly as the user drags the noodle across the canvas.
        """
        point = self.mapToScene(pos)
        if isinstance(self.attribute, OutputAttribute):
            self.newLine.pointB = point
        elif isinstance(self.attribute, InputAttribute):
            self.newLine.pointA = point

    def connectToItem(self, item):
        """
        Attempts to connect two items to eachother.
        Checks are made that the two graphical items are compatible (ie, two Sockets),
        and that the connection is legal on the backend (ie, Nuke nodes and ComprenderActions)
        """
        logger.debug("Trying to connect to item")
        ## Check that we're actually dealing with an input/output pair
        if isinstance(self.attribute, OutputAttribute) and isinstance(item.attribute, InputAttribute):
            fro = self
            to = item
        elif isinstance(self.attribute, InputAttribute) and isinstance(item.attribute, OutputAttribute):
            fro = item
            to = self
        else:
            logger.debug("Items not input/output pair")
            return False

        ## Check legality
        if not to.attribute.isLegalConnection(fro.attribute):
            logger.debug("Illegal connection")
            return False

        if not self.newLine:
            self.createNewLine()
        self.newLine.pointA = fro.getCenter()
        self.newLine.pointB = to.getCenter()
        self.newLine.source = fro
        self.newLine.target = to

        if isinstance(to.attribute, ArrayInputAttribute):
            to.attribute.value.append(fro.parentItem().node)
            to.inLines.append(self.newLine)
        else:
            to.attribute.value = fro.parentItem().node
            to.clearInLines()
            to.inLines.append(self.newLine)

        if self.newLine not in fro.outLines:
            fro.outLines.append(self.newLine)

        self.newLine.updatePath()
        self.newLine = None
        self.scene().update()

        return True

    def removeNewLine(self):
        """
        Cleans up the temp line, making sure we don't
        have any lingering items in the scene, leaking memory
        or newLine pointers refering to connected LineItems.
        """
        logger.debug("Removing temp line")
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
        if isinstance(item, NodeSocket):
            self.connectToItem(item)
        elif item is self.newLine:
            self.showCreateNodeMenu(event)
        if self.newLine:
            self.removeNewLine()

    def showCreateNodeMenu(self, event):
        menu = self.parent.createNodeMenu(self, event)
        selectedAction = menu.exec_(event.screenPos())

    def getCenter(self):
        rect = self.boundingRect()
        center = QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
        center = self.mapToScene(center)
        return center

    def clearInLines(self):
        for line in self.inLines:
            self.scene().removeItem(line)
        self.inLines = []

class NodeItem(QGraphicsItem):
    def __init__(self, node=None):
        super(NodeItem, self).__init__()
        self.node = node

        self.inputs = []
        self.outputs = []

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

        inputs = self.node.inputs()
        for attribute in inputs:
            socket =  NodeSocket(QRect(
                                        -socketSize/2,
                                        self.rect.height()/(len(inputs)+1) - socketSize/2,
                                        socketSize,
                                        socketSize
                                        ), self, attribute)
            self.inputs.append(socket)

        outputs = self.node.outputs()
        for attribute in outputs:
            socket = NodeSocket(QRect(
                                        self.rect.width()-socketSize/2,
                                        self.rect.height()/(len(outputs)+1) - socketSize/2,
                                        socketSize,
                                        socketSize), self, attribute)
            self.outputs.append(socket)

    def graphChanged(self):
        """
        Called when the graph changed. This might be better
        handled as connected attributes, but this way felt
        less intrusive.
        """
        self.prepareGeometryChange()
        x = self.node["pos.x"].value
        y = self.node["pos.y"].value
        logger.debug("Setting pos: {}.{}".format(str(x),str(y)))
        self.setPos(x, y)

        self.connectInputs()

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
        
        ## Draw node border
        painter.drawRoundedRect(self.rect, 5.0, 5.0)
       
        ## Set up text drawing
        font = painter.font()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(Qt.black)
        textMargin = 8

        ## Node Name
        painter.drawText(self.rect.adjusted(0,textMargin,-5,-textMargin), Qt.AlignHCenter | Qt.AlignTop, self.node.name)

        ## Node path
        painter.drawText(self.rect.adjusted(0,textMargin,-5,-textMargin), Qt.AlignHCenter | Qt.AlignBottom, self.node.visualName())

    def mouseMoveEvent(self, event):
        super(NodeItem, self).mouseMoveEvent(event)
        for output in self.outputs:
            for line in output.outLines:
                line.pointA = line.source.getCenter()
                line.pointB = line.target.getCenter()
        for inpt in self.inputs:
            for line in inpt.inLines:
                line.pointA = line.source.getCenter()
                line.pointB = line.target.getCenter()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.node:
                self.node["pos.x"].value = self.pos().x()
                self.node["pos.y"].value = self.pos().y()
        return QGraphicsItem.itemChange(self, change, value)

    def connectInputs(self):
        for input in self.inputs:
            if not input.attribute.value:
                continue
            logger.debug("Creating input connection")
            items = self.scene().items()
            item = None
            for x in items:
                if isinstance(x, NodeItem):
                    if x.node == input.attribute.value:
                        item = x
            if not item:
                logger.error("Couldn't find item by name: " + str(input.attribute.value.name))

            ## TODO: We should connect to attributes and not nodes..
            ## But this should work as long for single output nodes
            output = item.outputs[0] 

            exists = False
            for line in input.inLines:
                if line.source == output:
                    exists = True

            if exists:
                continue

            input.connectToItem(output)

    def getBaseColor(self, hue):
        return QColor.fromHsv(hue,120,100)

    def getTopColor(self, color):
        return color.lighter(150)

class SceneNodeItem(NodeItem):
    def __init__(self, node):
        super(SceneNodeItem, self).__init__(node)
        logger.debug("Creating SceneNodeItem")
       
        gradient = QLinearGradient(0,0,0,self.rect.height())
        baseCol = self.getBaseColor(0)
        gradient.setColorAt(1,baseCol)
        gradient.setColorAt(0,self.getTopColor(baseCol))
        self.brush = QBrush(gradient)
        logger.debug("Created SceneNodeItem")

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('Create on disk')
        listAction = menu.addAction('List versions')
        actionMenu = menu.addMenu("Create Action")
        for actionName in self.node.knownActions():
            action = QAction(actionName, self.scene())
            action.triggered.connect(
                    lambda checked, name=actionName: self.createAction(name))
            actionMenu.addAction(action) 
        selectedAction = menu.exec_(event.globalPos())

    def createNodeMenu(self, socket, event):
        menu = QMenu()
        actionMenu = menu.addMenu("Create Action")
        for actionName in self.node.knownActions():
            action = QAction(actionName, self.scene())
            action.triggered.connect(
                    lambda checked, name=actionName: self.createAction(name))
            actionMenu.addAction(action) 
        return menu

    def createAction(self, actionType):
        logger.debug("Attempting to create action: " + actionType)
        action = self.node.createAction(actionType, "")
        action["pos.x"].value = self.node["pos.x"].value + 200
        action["pos.y"].value = self.node["pos.y"].value
        ## TODO: Cleaner way of doing this:
        self.node.graph.graphChanged()

class ActionNodeItem(NodeItem):
    def __init__(self, node):
        super(ActionNodeItem, self).__init__(node)
        logger.debug("Creating ActionNodeItem")
       
        gradient = QLinearGradient(0,0,0,self.rect.height())
        baseCol = self.getBaseColor(120)
        gradient.setColorAt(1,baseCol)
        gradient.setColorAt(0,self.getTopColor(baseCol))
        self.brush = QBrush(gradient)
        logger.debug("Created ActionNodeItem")

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('Run in tractor')
        selectedAction = menu.exec_(event.globalPos())

    def createNodeMenu(self, socket, event):
        menu = QMenu()
        menu.addAction('I am an Action!') 
        return menu

class DataNodeItem(NodeItem):
    def __init__(self, node):
        super(DataNodeItem, self).__init__(node)
        logger.debug("Creating DataNodeItem")
       
        gradient = QLinearGradient(0,0,0,self.rect.height())
        baseCol = self.getBaseColor(240)
        gradient.setColorAt(1,baseCol)
        gradient.setColorAt(0,self.getTopColor(baseCol))
        self.brush = QBrush(gradient)
        logger.debug("Created DataNodeItem")

    def contextMenuEvent(self, event):
        menu = QMenu()
        make = menu.addAction('List versions')
        selectedAction = menu.exec_(event.globalPos())

    def createNodeMenu(self, socket, event):
        menu = QMenu()
        menu.addAction('I am data!') 
        return menu

