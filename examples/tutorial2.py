import sys

import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets


'''
============================================================
---   GRAPHICS CLASSES
============================================================
'''
class NodeLine(QtWidgets.QGraphicsPathItem):
    def __init__(self, pointA, pointB):
        super(NodeLine, self).__init__()
        self._pointA = pointA
        self._pointB = pointB
        self._source = None
        self._target = None
        self.setZValue(-1)
        self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(2)
        self.pen.setColor(QtGui.QColor(255,20,20,255))
        self.setPen(self.pen)

    def mousePressEvent(self, event):
        self.pointB = event.pos()

    def mouseMoveEvent(self, event):
        self.pointB = event.pos()

    def updatePath(self):
        path = QtGui.QPainterPath()
        path.moveTo(self.pointA)
        dx = self.pointB.x() - self.pointA.x()
        dy = self.pointB.y() - self.pointA.y()
        ctrl1 = QtCore.QPointF(self.pointA.x() + dx * 0.25, self.pointA.y() + dy * 0.1)
        ctrl2 = QtCore.QPointF(self.pointA.x() + dx * 0.75, self.pointA.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, self.pointB)
        self.setPath(path)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawPath(self.path())

    @property
    def pointA(self):
        return self._pointA

    @pointA.setter
    def pointA(self, point):
        self._pointA = point
        self.updatePath()

    @property
    def pointB(self):
        return self._pointB

    @pointB.setter
    def pointB(self, point):
        self._pointB = point
        self.updatePath()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, widget):
        self._source = widget

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, widget):
        self._target = widget


class NodeSocket(QtWidgets.QGraphicsItem):
    def __init__(self, rect, parent, socketType):
        super(NodeSocket, self).__init__(parent)
        self.rect = rect
        self.type = socketType

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtGui.QColor(180,20,90,255))

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(20,20,20,255))

        # Lines.
        self.outLines = []
        self.inLines = []

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def mousePressEvent(self, event):
        if self.type == 'out':
            rect = self.boundingRect()
            pointA = QtCore.QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointA = self.mapToScene(pointA)
            pointB = self.mapToScene(event.pos())
            self.newLine = NodeLine(pointA, pointB)
            self.outLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        elif self.type == 'in':
            rect = self.boundingRect()
            pointA = self.mapToScene(event.pos())
            pointB = QtCore.QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
            pointB = self.mapToScene(pointB)
            self.newLine = NodeLine(pointA, pointB)
            self.inLines.append(self.newLine)
            self.scene().addItem(self.newLine)
        else:
            super(NodeSocket, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.type == 'out':
            pointB = self.mapToScene(event.pos())
            self.newLine.pointB = pointB
        elif self.type == 'in':
            pointA = self.mapToScene(event.pos())
            self.newLine.pointA = pointA
        else:
            super(NodeSocket, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        item = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())
        if self.type == 'out' and item.type == 'in':
            self.newLine.source = self
            self.newLine.target = item
            item.parentItem().Input.inLines.append(self.newLine)
            self.newLine.pointB = item.getCenter()
        elif self.type == 'in' and item.type == 'out':
            self.newLine.source = item
            self.newLine.target = self
            item.parentItem().Output.outLines.append(self.newLine)
            self.newLine.pointA = item.getCenter()
        else:
            super(NodeSocket, self).mouseReleaseEvent(event)

    def getCenter(self):
        rect = self.boundingRect()
        center = QtCore.QPointF(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
        center = self.mapToScene(center)
        return center


class NodeItem(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(NodeItem, self).__init__()
        self.name = None
        self.rect = QtCore.QRect(0,0,100,60)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.initUi()

        # Brush.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(QtGui.QColor(80,0,90,255))

        # Pen.
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setWidth(1)
        self.pen.setColor(QtGui.QColor(20,20,20,255))

        self.selPen = QtGui.QPen()
        self.selPen.setStyle(QtCore.Qt.SolidLine)
        self.selPen.setWidth(1)
        self.selPen.setColor(QtGui.QColor(0,255,255,255))

    def initUi(self):
        self.Input = NodeSocket(QtCore.QRect(-10,20,20,20), self, 'in')
        self.Output = NodeSocket(QtCore.QRect(90,20,20,20), self, 'out')

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        return QtCore.QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        if self.isSelected():
            painter.setPen(self.selPen)
        else:
            painter.setPen(self.pen)
        painter.drawRect(self.rect)

    def mouseMoveEvent(self, event):
        super(NodeItem, self).mouseMoveEvent(event)
        for line in self.Output.outLines:
            line.pointA = line.source.getCenter()
            line.pointB = line.target.getCenter()
        for line in self.Input.inLines:
            line.pointA = line.source.getCenter()
            line.pointB = line.target.getCenter()

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        make = menu.addAction('make')
        makeFromHere = menu.addAction('make from here')
        debugConnections = menu.addAction('debug connections')
        selectedAction = menu.exec_(event.screenPos())

        #
        #if selectedAction == debugConnections:
        #    print('Input')
        #    for idx,line in enumerate(self.Input.inLines):
        #        print('  Line {0}'.format(idx))
        #        print('    pointA: {0}'.format(line.pointA))
        #        print('    pointB: {0}'.format(line.pointB))
        #    print('Output')
        #    for idx,line in enumerate(self.Output.outLines):
        #        print('  Line {0}'.format(idx))
        #        print('    pointA: {0}'.format(line.pointA)
        #        print('    pointB: {0}'.format(line.pointB))

class NodeView(QtWidgets.QGraphicsView):
    """
    QGraphicsView for displaying the nodes.

    :param scene: QGraphicsScene.
    :param parent: QWidget.
    """
    def __init__(self, scene, parent):
        super(NodeView, self).__init__(parent)
        self.setObjectName('View')
        self.setScene(scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.drag = False

    def wheelEvent(self, event):
        """
        Zooms the QGraphicsView in/out.

        :param event: QGraphicsSceneWheelEvent.
        """
        inFactor = 1.25
        outFactor = 1 / inFactor
        oldPos = self.mapToScene(event.pos())
        if event.delta():
            zoomFactor = inFactor
        else:
            zoomFactor = outFactor
        self.scale(zoomFactor, zoomFactor)
        newPos = self.mapToScene(event.pos())
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton and event.modifiers() == QtCore.Qt.AltModifier:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.drag = True
            self.prevPos = event.pos()
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        super(NodeView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag:
            delta = (self.mapToScene(event.pos()) - self.mapToScene(self.prevPos)) * -1.0
            center = QtCore.QPoint(self.viewport().width()/2 + delta.x(), self.viewport().height()/2 + delta.y())
            newCenter = self.mapToScene(center)
            self.centerOn(newCenter)
            self.prevPos = event.pos()
            return
        super(NodeView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag:
            self.drag = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(NodeView, self).mouseReleaseEvent(event)


'''
============================================================
---   UI CLASSES
============================================================
'''
class SideBar(QtWidgets.QFrame):
    def __init__(self, parent):
        super(SideBar, self).__init__(parent)
        self.setObjectName('SideBar')
        self.initUi()

    def initUi(self):
        # Frame.
        self.setFixedWidth(200)

        # Central Layout.
        self.CentralLayout = QtWidgets.QVBoxLayout(self)

        # Buttons.
        self.AddBoxButton = QtWidgets.QPushButton('Add Box')
        self.CentralLayout.addWidget(self.AddBoxButton)

        # Connections.
        self.initConnections()

    def initConnections(self):
        self.AddBoxButton.clicked.connect(self.clickedAddBoxButton)

    def clickedAddBoxButton(self):
        window = self.window()
        box = NodeItem()
        window.Scene.addItem(box)
        box.setPos(window.Scene.width()/2, window.Scene.height()/2)


class NodeWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(NodeWindow, self).__init__(parent)
        self.setWindowTitle('Node Window')
        self.initUi()

    def initUi(self):
        # Window.
        self.setMinimumSize(400,200)

        # Central Widget.
        self.CentralWidget = QtWidgets.QFrame()
        self.CentralWidget.setObjectName('CentralWidget')
        self.setCentralWidget(self.CentralWidget)

        # Central Layout.
        self.CentralLayout = QtWidgets.QHBoxLayout(self.CentralWidget)

        # GraphicsView.
        self.Scene = QtWidgets.QGraphicsScene()
        self.Scene.setObjectName('Scene')
        self.Scene.setSceneRect(0,0,32000,32000)
        self.View = NodeView(self.Scene, self)
        self.CentralLayout.addWidget(self.View)

        # Side Bar.
        self.SideBar = SideBar(self)
        self.CentralLayout.addWidget(self.SideBar)

        # Color.
        self.initColor()

    def initColor(self):
        windowCss = '''
        QFrame {
            background-color: rgb(90,90,90);
            border: 1px solid rgb(90,70,30);
        }
        QFrame#SideBar {
            background-color: rgb(50,50,50);
            border: 1px solid rgb(255,255,255);
        }'''
        self.setStyleSheet(windowCss)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    nodeWindow = NodeWindow()
    nodeWindow.show()
    sys.exit(app.exec_())
