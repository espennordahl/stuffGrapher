from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core.attributes import *
from .commands import *

logger = logging.getLogger(__name__)

class AttributeEditor(QDockWidget):

    attributeChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Attribute Editor")
        self.undoStack = parent.undoStack

        scrollArea = QScrollArea()
        
        widget = QWidget()
        widget.setMinimumSize(300,100)
        widget.setMaximumSize(300,10000)

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

        ## First non hidden
        for attribute in node.attributes.values():
            if not attribute.hidden:
                groupLayout.addWidget(self._createAttributeWidget(attribute))

        groupLayout.addWidget(QLabel("Hidden"))

        ## Then hidden tab while debugging
        for attribute in node.attributes.values():
            if attribute.hidden:
                groupLayout.addWidget(self._createAttributeWidget(attribute))
 

    def _createAttributeWidget(self, attribute):
        logger.debug("Building UI for attribute: " + attribute.key)
        
        layout = QHBoxLayout()
        layout.addWidget(QLabel(attribute.key))

        ## String widget
        if isinstance(attribute, StringAttribute):
            valueWidget = QLineEdit(str(attribute.value))
            valueWidget.textChanged.connect(
                    lambda foo, attr=attribute: self.setAttribute(attr))
            layout.addWidget(valueWidget)
        ## Enum widget
        elif isinstance(attribute, EnumAttribute):
            valueWidget = QComboBox()
            valueWidget.addItems(attribute.elements)
            valueWidget.setCurrentText(str(attribute.value))
            valueWidget.currentTextChanged.connect(
                    lambda foo, attr=attribute: self.setAttribute(attr))
            layout.addWidget(valueWidget)
        ## Bool widget
        elif isinstance(attribute, BoolAttribute):
            valueWidget = QCheckBox()
            valueWidget.setChecked(attribute.value)
            valueWidget.stateChanged.connect(
                    lambda foo, attr=attribute: self.setAttribute(attr))
            layout.addWidget(valueWidget)
        else:
            layout.addWidget(QLabel(str(attribute.value)))
 
        widget = QWidget()
        widget.setStyleSheet(
	        """
		QComboBox::item:checked {
		height: 12px;
		border: 1px solid #32414B;
		margin-top: 0px;
		margin-bottom: 0px;
		padding: 4px;
		padding-left: 0px;
		}
		"""
        )


        widget.setLayout(layout)
        return widget

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clearLayout(child.layout())

    def setAttribute(self, attribute):
        command = SetAttributeCommand(  attribute,
                                        attribute.value,
                                        self.valueFromWidget(self.sender()))
        self.undoStack.push(command)
        self.attributeChanged.emit() 

    def valueFromWidget(self, widget):
        if isinstance(widget, QLineEdit):
            return str(widget.text())
        elif isinstance(widget, QComboBox):
            return widget.currentIndex()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
