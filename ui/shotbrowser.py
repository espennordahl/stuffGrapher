from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class ShotBrowser(QDockWidget):
    shotChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Shot Browser")

        self.list = QListWidget()
        self.setWidget(self.list)
        
        self.list.currentItemChanged.connect(self.currentItemChanged)

    def addShot(self, shotname):
        self.list.addItem(shotname)

    def currentItemChanged(self, current, previous):
        name = self.list.currentItem().text()
        self.shotChanged.emit(name)
