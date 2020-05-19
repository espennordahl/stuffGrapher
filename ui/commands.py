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

       
