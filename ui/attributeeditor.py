from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core.attributes import *

class AttributeEditor(QDockWidget):
    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Attribute Editor")
        scrollArea = QScrollArea()
        
        widget = QWidget()
        widget.setMinimumSize(300,100)

        self.layoutWidget = QVBoxLayout()
        self.layoutWidget.setAlignment(Qt.AlignTop)

        widget.setLayout(self.layoutWidget)
        scrollArea.setWidget(widget)

        self.setWidget(widget)

        self.setNodes([])

    def setNodes(self, nodes):
        self.clearLayout(self.layoutWidget)
        for node in nodes:
            self._createNodeUI(node)
        if not nodes:
            self.layoutWidget.addWidget(QLabel("No node selected"))
   
    def _createNodeUI(self, node):
        groupbox = QGroupBox(node.name)
        self.layoutWidget.addWidget(groupbox)

        groupLayout = QVBoxLayout()
        groupbox.setLayout(groupLayout)

        for attribute in node.attributes.values():
            groupLayout.addWidget(self._createAttributeWidget(attribute))

        

    def _createAttributeWidget(self, attribute):
        logging.debug("Building UI for attribute: " + attribute.key)
        
        layout = QHBoxLayout()
        layout.addWidget(QLabel(attribute.key))
        layout.addWidget(QLabel(str(attribute.value)))
 
        widget = QWidget()
        widget.setLayout(layout)
        return widget


    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clearLayout(child.layout())
