import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import Graph, SceneFile, Action, Data
from core.attributes import *

from .commands import *
from .nodeline import NodeLine
from .nodesocket import NodeSocket

logger = logging.getLogger(__name__)

class NodeItem(QGraphicsItem):
    def __init__(self, controller, node=None):
        super(NodeItem, self).__init__()

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.controller = controller
        self.oldPos = self.pos()
        self.updating = False
        self.moving = False

        self.node = node

        self.inputs = []
        self.outputs = []

        textWidth = len(node.name) * 10
        nodeWidth = max(100, min(textWidth, 200))
        self.rect = QRect(0,0,nodeWidth,50)
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
        self.updating = True
        
        x = self.node["pos.x"].value
        y = self.node["pos.y"].value
        logger.debug("Setting pos: {} , {}".format(str(x),str(y)))
        
        self.setPos(x, y)

        self.connectInputs()

        for socket in self.inputs + self.outputs:
            socket.positionChanged()
        
        self.updating = False

    def removedFromScene(self):
        for input in self.inputs:
            for line in input.inLines:
                line.source.itemRemovedFromScene(self)

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
        if self.node and self.moving:
            point = self.mapToScene(event.pos()) + self.mouseOffset
            moveCommand = SetPositionCommand(   self,
                                                self.oldPos.x(),
                                                self.oldPos.y(),
                                                point.x(),
                                                point.y())
            self.controller.undoStack.push(moveCommand)

        for output in self.outputs:
            for line in output.outLines:
                #TODO: This feels silly..
                line.pointA = line.source.getCenter()
                line.pointB = line.target.getCenter()
        for inpt in self.inputs:
            for line in inpt.inLines:
                #TODO: This feels silly..
                line.pointA = line.source.getCenter()
                line.pointB = line.target.getCenter()

    def mousePressEvent(self, event):
        self.oldPos = self.pos()
        self.mouseOffset = self.pos() - self.mapToScene(event.pos())
        self.moving = True
        return QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.oldPos = self.pos()
        self.moving = False
        return QGraphicsItem.mouseReleaseEvent(self, event)

    def connectInputs(self):
        for input in self.inputs:
            if not input.attribute.value:
                continue
            if isinstance(input.attribute, ArrayInputAttribute):
                inputNodes = input.attribute.value
            else:
                inputNodes = [input.attribute.value]

            for inputNode in inputNodes:
                logger.debug("Creating input connection: {}<--{}".format(self.node.name, inputNode.name))
                items = self.scene().items()
                item = None
                for x in items:
                    if isinstance(x, NodeItem):
                        if x.node == inputNode:
                            item = x
                if not item:
                    logger.error("Couldn't find item by name: " + str(inputNode.name))
                    raise Exception

                ## TODO: We should connect to attributes and not nodes..
                ## But this should work as long for single output nodes
                output = item.outputs[0] 

                exists = False
                for line in input.inLines:
                    if line.source == output:
                        exists = True

                if exists:
                    logger.debug("Connection exists. Skipping")
                    continue

                input.connectToItem(output)

    def getBaseColor(self, hue):
        return QColor.fromHsv(hue,120,100)

    def getTopColor(self, color):
        return color.lighter(150)

    def getOutputNodePos(self):
        pos = QPointF(self.node["pos.x"].value, self.node["pos.y"].value)
        pos.setX(pos.x() + 200)

        while self.scene().itemAt(pos, QTransform()):
            pos.setY(pos.y() + 100)
 
        return pos

class SceneNodeItem(NodeItem):
    def __init__(self, controller, node):
        super(SceneNodeItem, self).__init__(controller, node)
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
        pos = self.getOutputNodePos()
        createCommand = CreateActionFromSceneCommand(self.node, actionType, pos)
        self.controller.undoStack.push(createCommand)

class ActionNodeItem(NodeItem):
    def __init__(self, controller, node):
        super(ActionNodeItem, self).__init__(controller, node)
        logger.debug("Creating ActionNodeItem")
       
        gradient = QLinearGradient(0,0,0,self.rect.height())
        baseCol = self.getBaseColor(120)
        gradient.setColorAt(1,baseCol)
        gradient.setColorAt(0,self.getTopColor(baseCol))
        self.brush = QBrush(gradient)
        logger.debug("Created ActionNodeItem")

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction('Run in Tractor')
        dataMenu = menu.addMenu("Create Data")
        for dataName in self.node.knownData():
            action = QAction(dataName, self.scene())
            action.triggered.connect(
                    lambda checked, name=dataName: self.createData(name))
            dataMenu.addAction(action) 
        selectedAction = menu.exec_(event.globalPos())

    def createNodeMenu(self, socket, event):
        menu = QMenu()
        dataMenu = menu.addMenu("Create Data")
        for dataName in self.node.knownData():
            action = QAction(dataName, self.scene())
            action.triggered.connect(
                    lambda checked, name=dataName: self.createData(name))
            dataMenu.addAction(action) 
        return menu

    def createData(self, datatype):
        logger.debug("Attempting to create data")
        pos = self.getOutputNodePos()
        createCommand = CreateDataFromActionCommand(self.node, datatype, pos)
        self.controller.undoStack.push(createCommand)

class DataNodeItem(NodeItem):
    def __init__(self, controller, node):
        super(DataNodeItem, self).__init__(controller, node)
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

