import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import Graph, SceneFile, Action, Data
from core.attributes import *

from .commands import *
from .nodeline import NodeLine

logger = logging.getLogger(__name__)

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

    def itemRemovedFromScene(self, removeditem):
        for line in self.outLines:
            if line.target in removeditem.inputs:
                self.scene().removeItem(line)

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
            raise Exception
 
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
            logger.debug("{}: NewLine doesn't exist. Creating".format(self.parent.node.name))
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
        logger.debug("Setting newLine to None")
        self.newLine = None
        self.scene().update()

        return True

    def removeNewLine(self):
        """
        Cleans up the temp line, making sure we don't
        have any lingering items in the scene, leaking memory
        or newLine pointers refering to connected LineItems.
        """
        logger.debug("{}: Removing temp line".format(self.parent.node.name))
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
        logger.debug("Mouse Released")
        item = self.scene().itemAt(event.scenePos().toPoint(), QTransform())
        if isinstance(item, NodeSocket):
            self.attemptConnection(item)
        elif item is self.newLine:
            self.showCreateNodeMenu(event)
        if self.newLine:
            self.removeNewLine()


    def attemptConnection(self, item):
        ## Check that we're actually dealing with an input/output pair
        if isinstance(self.attribute, OutputAttribute) and isinstance(item.attribute, InputAttribute):
            fro = self
            to = item
        elif isinstance(self.attribute, InputAttribute) and isinstance(item.attribute, OutputAttribute):
            fro = item
            to = self
        else:
            logger.debug("Items not input/output pair")
            return

        ## Check legality
        if not to.attribute.isLegalConnection(fro.attribute):
            logger.debug("Illegal connection")
            return

        
        if isinstance(to.attribute, ArrayInputAttribute):
            command = AddConnectionCommand(fro.parentItem().node, to.attribute)
        else:
            command = CreateConnectionCommand(fro.parentItem().node, to.attribute)
        
        self.parent.controller.undoStack.push(command)


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
            if line is not self.newLine:
                self.scene().removeItem(line)
        self.inLines = []

    def positionChanged(self):
        for line in self.inLines + self.outLines:
            ##TODO: This should really not be nessecary..
            if line.source:
                line.pointA = line.source.getCenter()
            if line.target:
                line.pointB = line.target.getCenter()


