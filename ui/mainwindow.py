import sys
import logging
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import qdarkstyle

from .attributeeditor import AttributeEditor
from .shotbrowser import ShotBrowser
from .nodegraph import *

from core import Shot
from core import Graph
from core import Project

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.project = Project()
        
        self.setWindowTitle("StuffGrapher")
        self._initUI()
        self._initMenuBar()

        self.show()

    def _initUI(self):
        # Status Bar
        self.statusBar().showMessage("Ready")
        
        # Window Size
        self.setMinimumSize(400, 400)
        self.setGeometry(0, 0, 1920, 1080)

        # NodeGraph
        self.centralWidget = QFrame()
        self.setCentralWidget(self.centralWidget)

        self.centralLayout = QVBoxLayout(self.centralWidget)

        self.graphLabel = QLabel("No shot selected")
        self.centralLayout.addWidget(self.graphLabel, alignment=Qt.AlignCenter)

        self.nodeGraph = NodeGraphView(self)
        self.nodeGraph.mainWindow = self
        self.centralLayout.addWidget(self.nodeGraph)

        # Attribute Editor
        self.attributeEditor = AttributeEditor(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.attributeEditor)
        self.nodeGraph.selectionChanged.connect(self.attributeEditor.setNodes)
        self.attributeEditor.attributeChanged.connect(self.nodeGraph.scene().update)

        # Shot Browser
        self.shotBrowser = ShotBrowser(self.project, self)
        self.shotBrowser.shotChanged.connect(self.shotChanged)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.shotBrowser)


    def _initMenuBar(self):
        menuBar = self.menuBar()

        ## File menu
        self.fileMenu = menuBar.addMenu("File")

        ## Open
        openAction = QAction("Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip("Open File")
        openAction.triggered.connect(self.open)
        self.fileMenu.addAction(openAction)

        ## Save
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+s")
        saveAction.setStatusTip("Save File")
        saveAction.triggered.connect(self.save)
        self.fileMenu.addAction(saveAction)

        ## Save As
        saveAsAction = QAction("Save As", self)
        saveAsAction.setShortcut("Ctrl+S")
        saveAsAction.setStatusTip("Save File As")
        saveAsAction.triggered.connect(self.saveas)
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

        ## Shots menu
        self.shotMenu = menuBar.addMenu("Shots")

        ## Import shots 
        importSGAction = QAction("Import shots from Shotgun", self)
        importSGAction.setStatusTip("Import shots from Shotgun")
        importSGAction.triggered.connect(self.importShots)
        self.shotMenu.addAction(importSGAction)

        ## Node Menu
        self.nodeMenu = menuBar.addMenu("Nodes")
        self.buildCreateNodeMenu(self.nodeMenu)

        # Tractor Menu
        self.tractorMenu = menuBar.addMenu("Tractor")
        
        tractorScenefilesAction = QAction("Create Scenefile Templates", self)
        self.tractorMenu.addAction(tractorScenefilesAction)

        tractorActionsAction = QAction("Run Actions", self)
        self.tractorMenu.addAction(tractorActionsAction)

        tractorDataAction = QAction("Generate Data", self)
        self.tractorMenu.addAction(tractorDataAction)

    def buildCreateNodeMenu(self, menu):
        
        ## Actions
        actionsMenu = menu.addMenu("Actions")
        actions = [
                    "Render",
                    "Comprender",
                    "PublishGeo",
                    "PublishLookdev",
                    "PublishGeocache"
                    ]
        for actionname in actions:
            action = QAction(actionname, self)
            action.setStatusTip("Create {node}".format(node=actionname))
            action.triggered.connect(
                                lambda checked, name=actionname + "Action": self.createNode(name))
            actionsMenu.addAction(action)

        sceneMenu = menu.addMenu("Scenes")
        scenes  = [
                        "Maya",
                        "Houdini",
                        "Nuke"
                    ]
        for scenename in scenes:
            action = QAction(scenename, self)
            action.setStatusTip("Create {node}".format(node=scenename))
            action.triggered.connect(
                                lambda checked, name=scenename + "File": self.createNode(name))
            sceneMenu.addAction(action)

        dataMenu = menu.addMenu("Data")
        datatypes = [
                    "Geo",
                    "Geocache",
                    "Lookdev",
                    "Plate",
                    "Render",
                    "Comprender"
                ]
        for dataname in datatypes:
            action = QAction(dataname, self)
            action.setStatusTip("Create {node}".format(node=dataname))
            action.triggered.connect(
                                lambda checked, name=dataname + "Data": self.createNode(name))
            dataMenu.addAction(action)




    def createNode(self, classname):
        self.nodeGraph.createNode(classname)

    def importShots(self):
        tempshots = [
                        "fx010",
                        "fx020",
                        "fx030",
                        "fx040",
                        "fx100",
                        "fx120",
                        "vg040",
                        "vg045",
                        "vg080"
                        ]
        for shotname in tempshots:
            shot = Shot(shotname)
            shot.graph = Graph()
            self.shotBrowser.addShot(shot)

    def shotChanged(self, shotname):
        shot = self.project.shots[shotname]
        if shot.parent:
            labelText = "{} <{}>".format(shot.name, shot.parent.name)
        else:
            labelText = shot.name
        self.graphLabel.setText(labelText)
        self.nodeGraph.setShot(self.project.shots[shotname])

    def save(self):
        self.saveas()

    def saveas(self):
        data = self.project.serialize()
        filename = QFileDialog.getSaveFileName(self, "Save Project", "/Users/espennordahl/Desktop", "Projects (*.sg)")[0]
        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent=4)

    def open(self):
        filename = QFileDialog.getOpenFileName(self, "Open Project", "/Users/espennordahl/Desktop", "Projects (*.sg)")[0]
        with open(filename) as infile:
            data = json.load(infile)

        self.clearProject()
        self.project = Project.deserialize(data)
        self.shotBrowser.setProject(self.project)

    def clearProject(self):
        return
