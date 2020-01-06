from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class AttributeEditor(QDockWidget):
    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Attribute Editor")
        listWidget = QListWidget()
        listWidget.addItem("Attr")
        listWidget.addItem("Attr")
        listWidget.addItem("Foo")
        listWidget.addItem("Bar")
        self.setWidget(listWidget)


