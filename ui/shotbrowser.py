import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import Shot, Graph

logger = logging.getLogger(__name__)

class ShotItem(QTreeWidgetItem):
    def __init__(self, parent, shot):
        super(ShotItem, self).__init__(parent)
        self.clipboard = parent.graphClipboard
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
        self.shot = shot
        self.setText(0, self.shot.name)

    def populateRightClickMenu(self, menu):
        clearAction = menu.addAction("Clear Graph")
        clearAction.triggered.connect(self.clearGraph)

        copyAction = menu.addAction("Copy Graph")
        copyAction.triggered.connect(self.copyGraph)

        pasteAction = menu.addAction("Paste Graph")
        pasteAction.triggered.connect(self.pasteGraph)

    def clearGraph(self):
        self.shot.graph.clear()

    def copyGraph(self):
        self.clipboard["graph"] = self.shot.graph.serialize()
        logger.debug("Clipped graph: {}".format(self.clipboard))

    def pasteGraph(self):
        if self.clipboard:
            self.shot.graph.clear()
            self.shot.graph.paste(self.clipboard["graph"])
            self.shot.graph.graphChanged()
        else:
            logger.debug("No clipboard")

class TemplateItem(QTreeWidgetItem):
    def __init__(self, parent, name):
        super(TemplateItem, self).__init__(parent)
        self.setFlags(
                        Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEditable
                    )

        self.setForeground(0, QBrush(QColor("black")))
        self.setBackground(0, QBrush(QColor("grey")))
        self.shot = Shot(name)
        self.shot.graph = Graph()
        self.setText(0, self.shot.name)

    def populateRightClickMenu(self, menu):
        return

class ShotTreeWidget(QTreeWidget):
    def __init__(self):
        super(ShotTreeWidget, self).__init__()
        ##TODO: Better clipboard handling
        self.graphClipboard = {"graph": None}

        ## Make sure we can drag/drop shots into templates
        self.setColumnCount(1)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSortingEnabled(True)

        ## right click menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)

    def rightClickMenu(self, event):
        menu = QMenu(self)
        selection = self.selectedItems()
        if selection:
            selection[0].populateRightClickMenu(menu)
        menu.exec_(self.mapToGlobal(event))

    def dropEvent(self, event):
        """
        Triggered when an item is released through drag/drop.
        We allow shots to be dragged into templates, otherwise
        we ignore it.
        """
        super(ShotTreeWidget, self).dropEvent(event)
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if isinstance(item, ShotItem):
                parent = item.parent()
                if isinstance(parent, TemplateItem):
                    item.shot.parent = parent.shot
                else:
                    item.shot.parent = None
                
            iterator += 1


class ShotBrowser(QDockWidget):
    shotChanged = pyqtSignal(str)

    def __init__(self, project, parent=None):
        super(QDockWidget, self).__init__("Shot Browser")

        self.shots = project.shots
        self.templates = project.templates

        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)
 
        self.tree = ShotTreeWidget()
        layout.addWidget(self.tree)

        ## Template button
        templateButton = QPushButton("Create Template")
        templateButton.clicked.connect(self.createTemplate)

        layout.addWidget(templateButton)

        self.tree.currentItemChanged.connect(self.currentItemChanged)
        self.tree.itemChanged.connect(self.itemChanged)

    def setProject(self, project):
        self.shots = project.shots
        self.templates = project.templates

        self.tree.clear()

        for shot in self.shots.values():
            item = ShotItem(self.tree, shot)

        for template in self.templates:
            item = TemplateItem(self.tree, template)

    def createTemplate(self):
        """
        Creates a new template. 
        Templates contain graphs that are shared between shots.
        """
        basename = "template"
        i = 1
        name = basename + str(i)
        while name in self.templates:
            i += 1
            name = basename+str(i)

        template = TemplateItem(self.tree, name)
        self.templates[name] = template

    def addShot(self, shot):
        """
        Adds a shot to the list
        """
        item = ShotItem(self.tree, shot)
        self.shots[shot.name] = shot

    def currentItemChanged(self, current, previous):
        """
        Triggered when an item is selected. 
        """
        item = self.tree.currentItem()
        if isinstance(item, ShotItem):
            self.shotChanged.emit(item.shot.name)

    def itemChanged(self, item, column):
        if isinstance(item, TemplateItem):
            if item in self.templates.values():
                del self.templates[item.shot.name]
                name = item.text(0)
                i = 1
                while name in self.templates:
                    name = name + str(i)
                    i += 1
                item.setText(0, name)
                item.shot.name = name
                self.templates[name] = item

