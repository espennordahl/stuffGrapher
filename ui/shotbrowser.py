from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

testshots = {   "fx": [
                "fx010", 
                "fx020",
                "fx030"],
                "db": [
                "db010",
                "db020",
                "db050",
                "db060"]
                }

class TreeModel(QAbstractItemModel):
    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.nodes = ['node0', 'node1', 'node2', 'node3', 'node4', 'node5']

    def index(self, row, column, parent):
        if row < 0 or row >= len(self.nodes):
            return QModelIndex()
        return self.createIndex(row, column, self.nodes[row])

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, index):
        if index.isValid():
            return 0
        if index.internalPointer() in self.nodes:
            return 0
        return len(self.nodes)

    def columnCount(self, index):
        if index.isValid():
            return 0
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == 0: 
            return index.internalPointer()
        else:
            return None

    def supportedDropActions(self): 
        return Qt.CopyAction | Qt.MoveAction         

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled        

    def insertRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        # inserting 'count' empty rows starting at 'row'
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        for i in range(0, count):
            self.nodes.insert(row + i, '')
        self.endInsertRows()
        return True

    def removeRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        num_rows = self.rowCount(QModelIndex())
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        for i in range(count, 0, -1):
            self.nodes.pop(row - i + 1)
        self.endRemoveRows()
        return True

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if index.row() < 0 or index.row() > len(self.nodes):
            return False
        self.nodes[index.row()] = str(value)
        self.dataChanged.emit(index, index)


class ShotBrowser(QDockWidget):
    def __init__(self, parent=None):
        super(QDockWidget, self).__init__("Shot Browser")

        self.tree = QTreeView(self)
        self.setWidget(self.tree)

        root_model = TreeModel()
        self.tree.setModel(root_model)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)


