import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import qdarkstyle


class AttributeEditor(QDockWidget):
    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Attribute Editor")
        listWidget = QListWidget()
        listWidget.addItem("Item")
        listWidget.addItem("Item")
        listWidget.addItem("Item")
        listWidget.addItem("Item")
        self.setWidget(listWidget)

class NodeView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(NodeView, self).__init__(parent)
        self.setScene(scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.drag = False



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

        # Central Widget.
        self.centralWidget = QFrame()
        self.setCentralWidget(self.centralWidget)

        # Central Layout.
        self.centralLayout = QHBoxLayout(self.centralWidget)

        # GraphicsView.
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0,0,32000,32000)
        self.view = NodeView(self.scene, self)
        self.centralLayout.addWidget(self.view)

        # Attribute Editor
        self.attributeEditor = AttributeEditor(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.attributeEditor)


    def _initMenuBar(self):
        menuBar = self.menuBar()

        ## File menu
        self.fileMenu = menuBar.addMenu("File")

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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWindow.show()

    sys.exit(app.exec_())
