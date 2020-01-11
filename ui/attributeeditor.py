from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class AttributeEditor(QDockWidget):
    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Attribute Editor")
        self.listWidget = QListWidget()
        self.listWidget.addItem("Attr")
        self.listWidget.addItem("Attr")
        self.listWidget.addItem("Foo")
        self.listWidget.addItem("Bar")
        self.setWidget(self.listWidget)

    def setNodes(self, nodes):
        self.listWidget.clear()
        for node in nodes:
            self.listWidget.addItem(node.name)
