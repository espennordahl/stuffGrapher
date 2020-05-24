import sys
import logging
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

logger = logging.getLogger(__name__)

class CreateNodeCommand(QUndoCommand):
    def __init__(self, classname, graph, pos, parent=None):
        QUndoCommand.__init__(self, parent)
        self._classname = classname
        self._nodegraph = graph
        self._pos = pos        
        self._node = None

    def undo(self):
        logger.info("Undoing Create Node")
        self._nodegraph.removeNode(self._node)
        self._nodegraph.graphChanged()

    def redo(self):
        logger.info("Creaating Node")
        if self._node:
            self._nodegraph.addNode(self._node)
        else:
            self._node = self._nodegraph.createNode(self._classname, "foo") 

        self._node["pos.x"].value = self._pos.x()
        self._node["pos.y"].value = self._pos.y()
        self._nodegraph.graphChanged()

class CreateDataFromActionCommand(QUndoCommand):
    def __init__(self, node, dataType, pos, parent=None):
        QUndoCommand.__init__(self, parent)
        self._classname = dataType 
        self._graph = node.graph
        self._pos = pos
        self._node = node
        self._dataNode = None

    def undo(self):
        logger.info("Undoing Create Data from Action")
        self._graph.removeNode(self._dataNode)
        self._graph.graphChanged()

    def redo(self):
        logger.info("Creating Data from Action")
        if self._dataNode:
            self._graph.addNode(self._dataNode)
        else:
            self._dataNode = self._node.createData(self._classname)

        self._dataNode["pos.x"].value = self._pos.x()
        self._dataNode["pos.y"].value = self._pos.y()
        self._graph.graphChanged()

class CreateActionFromSceneCommand(QUndoCommand):
    def __init__(self, node, actionType, pos, parent=None):
        QUndoCommand.__init__(self, parent)
        self._classname = actionType 
        self._graph = node.graph
        self._pos = pos
        self._node = node
        self._actionNode = None

    def undo(self):
        logger.info("Undoing Create Action from Node")
        self._graph.removeNode(self._actionNode)
        self._graph.graphChanged()

    def redo(self):
        logger.info("Creating Action from Node")
        if self._actionNode:
            self._graph.addNode(self._actionNode)
        else:
            self._actionNode = self._node.createAction(self._classname, "foo")

        self._actionNode["pos.x"].value = self._pos.x()
        self._actionNode["pos.y"].value = self._pos.y()
        self._graph.graphChanged()


class SetAttributeCommand(QUndoCommand):
    def __init__(self, attribute, oldValue, newValue, parent=None):
        QUndoCommand.__init__(self, parent)
        self._attribute = attribute
        self._oldValue = oldValue
        self._newValue = newValue

    def id(self):
        return 1337

    def mergeWith(self, other):
        if other.id() != self.id():
            return False
        if self._attribute != other._attribute:
            return False

        self._newValue = other._newValue
        return True

    def undo(self):
        logger.info("Undoing attribute value change")
        self._attribute.value = self._oldValue
        self._attribute.parent.graph.graphChanged()

    def redo(self):
        logger.info("Applying attribute value change")
        self._attribute.value = self._newValue
        self._attribute.parent.graph.graphChanged()

class SetPositionCommand(QUndoCommand):
    def __init__(self, item, oldX, oldY, newX, newY, parent=None):
        QUndoCommand.__init__(self, parent)
        self._item = item
        self._node = item.node
        self._oldX = oldX
        self._oldY = oldY
        self._newX = newX
        self._newY = newY

    def id(self):
        return self._oldX + self._oldY 

    def mergeWith(self, other):
        if other.id() != self.id():
            return False
        if self._node != other._node:
            return False
        
        self._newX = other._newX
        self._newY = other._newY
        return True

    def undo(self):
        logger.info("Undoing position change -> {} , {}".format(self._oldX, self._oldY))
        self._node["pos.x"] = self._oldX
        self._node["pos.y"] = self._oldY
        self._node.graph.graphChanged()

    def redo(self):
        logger.info("Applying position change -> {} , {}".format(self._newX, self._newY))
        self._node["pos.x"] = self._newX
        self._node["pos.y"] = self._newY
        self._node.graph.graphChanged()


class CreateConnectionCommand(QUndoCommand):
    def __init__(self, fromNode, toAttribute, parent=None):
        QUndoCommand.__init__(self, parent)
        self._toAttribute = toAttribute
        self._fromNodeNew = fromNode
        self._fromNodeOld = None
        if toAttribute.value:
            self._fromNode = toAttribute.value

    def redo(self):
        self._toAttribute.value = self._fromNodeNew
        self._fromNodeNew.graph.graphChanged()

    def undo(self):
        self._toAttribute.value = self._fromNodeOld
        self._fromNodeNew.graph.graphChanged()

class AddConnectionCommand(QUndoCommand):
    def __init__(self, fromNode, toAttribute, parent=None):
        QUndoCommand.__init__(self, parent)
        self._toAttrtibute = toAttribute
        self._fromNodeNew = fromNode

    def redo(self):
        self._toAttribute.value.append(self._fromNode)
        self._fromNode.graph.graphChanged()

    def undo(self):
        self._toAttribute.value.remove(self._fromNode)
        self._fromNode.graph.graphChanged()




class SwitchShotCommand(QUndoCommand):
    def __init__(self, fromShot, toShot, graphLabel, nodeGraph, shotBrowser, parent=None):
        QUndoCommand.__init__(self, parent)
        self._fromShot = fromShot
        self._toShot = toShot
        self._graphLabel = graphLabel
        self._nodeGraph = nodeGraph
        self._shotBrowser = shotBrowser

    def setShot(self, shot):
        if not shot:
            ##TODO: Set selection to none
            return
        if shot.parent:
            labelText = "{} <{}>".format(shot.name, shot.parent.name)
        else:
            labelText = shot.name
        self._graphLabel.setText(labelText)
        self._nodeGraph.setShot(shot)
        self._shotBrowser.setShot(shot.name)

    def undo(self): 
        logger.info("Undoing Switching shots")
        self.setShot(self._fromShot)

    def redo(self):
        logger.info("Switching shots")
        self.setShot(self._toShot)
