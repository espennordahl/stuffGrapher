import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import qdarkstyle

from .attributeeditor import AttributeEditor
from .shotbrowser import ShotBrowser
from .nodegraph import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("StuffGrapher")
        self._initUI()
        self._initMenuBar()
        self.show()

    def _initUI(self):
        # Status Bar
        self.statusBar().showMessage("Ready")
        
        # Window Size
        self.setMinimumSize(400, 400)
        self.setGeometry(100, 100, 1500, 900)

        # NodeGraph
        self.centralWidget = QFrame()
        self.setCentralWidget(self.centralWidget)

        self.centralLayout = QHBoxLayout(self.centralWidget)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0,0,32000,32000)
        self.nodeGraph = NodeGraphView(self.scene, self)
        self.centralLayout.addWidget(self.nodeGraph)

        # Attribute Editor
        self.attributeEditor = AttributeEditor(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.attributeEditor)

        # Shot Browser
        self.shotBrowser = ShotBrowser(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.shotBrowser)


    def _initMenuBar(self):
        menuBar = self.menuBar()

        ## File menu
        self.fileMenu = menuBar.addMenu("File")

        ## Create Node (Temp) 
        createAction = QAction("Create Node", self)
        createAction.setStatusTip("Create Node")
        createAction.triggered.connect(self.createNode)
        self.fileMenu.addAction(createAction)

        ## Open
        openAction = QAction("Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip("Open File")
        self.fileMenu.addAction(openAction)

        ## Save
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+s")
        saveAction.setStatusTip("Save File")
        self.fileMenu.addAction(saveAction)

        ## Save As
        saveAsAction = QAction("Save As", self)
        saveAsAction.setShortcut("Ctrl+S")
        saveAsAction.setStatusTip("Save File As")
        self.fileMenu.addAction(saveAsAction)

        ## Exit
        exitAction = QAction(" Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(exitAction)

        ## Edit Menu
        self.editMenu = menuBar.addMenu("Edit")

        ## Undo
        undoAction = QAction("Undo", self)
        undoAction.setShortcut("Ctrl+z")
        undoAction.setStatusTip("Undo")
        self.editMenu.addAction(undoAction)

        ## Redo
        redoAction = QAction("Redo", self)
        redoAction.setShortcut("Ctrl+y")
        redoAction.setStatusTip("Redo")
        self.editMenu.addAction(redoAction)

        ## Copy
        copyAction = QAction("Copy", self)
        copyAction.setShortcut("Ctrl+c")
        copyAction.setStatusTip("Copy selection")
        self.editMenu.addAction(copyAction)

        ## Cut
        cutAction = QAction("Cut", self)
        cutAction.setShortcut("Ctrl+x")
        cutAction.setStatusTip("Cut selection")
        self.editMenu.addAction(cutAction)

        ## Paste
        pasteAction = QAction("Paste", self)
        pasteAction.setShortcut("Ctrl+v")
        pasteAction.setStatusTip("Paste")
        self.editMenu.addAction(pasteAction)

    def createNode(self):
        self.nodeGraph.addNode(NodeItem())
