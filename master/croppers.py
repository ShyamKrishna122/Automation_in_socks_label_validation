from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtWidgets import QLabel


class Viewer(QtWidgets.QGraphicsView):
    def __init__(self, main, parent=None):
        super().__init__(QtWidgets.QGraphicsScene(), parent)
        self.pixmap_item = self.scene().addPixmap(QtGui.QPixmap())
        self.title = QLabel()
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

    def getModel(self, model):
        self.model = model

    def setPixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)


class QImageViewer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        self.view = Viewer(self)
        self.setCentralWidget(self.view)

        self.printer = QtPrintSupport.QPrinter()

        self.createMenus()
        self.showMaximized()

    def setModel(self, model):
        self.model = model
        self.view.getModel(self.model)

    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)

        self.fileMenu.addSeparator()
        self.menuBar().addMenu(self.fileMenu)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())
