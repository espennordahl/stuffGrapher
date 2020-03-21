from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core import Shot, Graph

class ShotItem(QTreeWidgetItem):
    def __init__(self, parent, shot):
        super(ShotItem, self).__init__(parent)
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
        self.shot = shot
        self.setText(0, self.shot.name)


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

class ShotTreeWidget(QTreeWidget):
    def __init__(self):
        super(ShotTreeWidget, self).__init__()

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

    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Shot Browser")

        self.shots = {}
        self.templates = {}

        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)
 
        ## Make sure we can drag/drop shots into templates
        self.tree = ShotTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.setDragEnabled(True)
        self.tree.viewport().setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree.setSortingEnabled(True)

        layout.addWidget(self.tree)

        ## Template button
        templateButton = QPushButton("Create Template")
        templateButton.clicked.connect(self.createTemplate)

        layout.addWidget(templateButton)

        self.tree.currentItemChanged.connect(self.currentItemChanged)
        self.tree.itemChanged.connect(self.itemChanged)

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

