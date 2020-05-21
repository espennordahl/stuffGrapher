import sys
import logging
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

logger = logging.getLogger(__name__)

class CreateNodeCommand(QUndoCommand):
    def __init__(self, classname, shot, pos, parent=None):
        QUndoCommand.__init__(self, parent)
        self._classname = classname
        self._nodegraph = shot.graph
        self._pos = pos        

    def undo(self):
        self._nodegraph.removeNode(self._node)
        self._nodegraph.graphChanged()

    def redo(self):
        self._node = self._nodegraph.createNode(self._classname, "foo") 
        self._node["pos.x"].value = self._pos.x()
        self._node["pos.y"].value = self._pos.y()
        self._nodegraph.graphChanged()

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
        self.setShot(self._fromShot)

    def redo(self):
        self.setShot(self._toShot)
