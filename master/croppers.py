from constants import Constants
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
import sqlite3
from _sqlite3 import Error
from PyQt5.QtGui import QPainter, QPen, QPixmap

from PyQt5.QtWidgets import QLabel, QLabel, QLineEdit, QVBoxLayout

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGridLayout, QHBoxLayout, QLabel, QLabel, QLineEdit, QVBoxLayout
import cv2


class Viewer(QtWidgets.QGraphicsView):

    def setFileName(self,fileName):
        self.fileName = fileName

    def saveImage(self):
        img = cv2.imread(self.fileName)
        cv2.imwrite(f"{Constants.master_image_path}{self.model}.jpg",img)

    def __init__(self,main, parent=None):
        super().__init__(QtWidgets.QGraphicsScene(), parent)
        self.pixmap_item = self.scene().addPixmap(QtGui.QPixmap())
        self.button = QtWidgets.QPushButton("Save All Features")
        self.button.clicked.connect(self.saveAllFeatures)
        self.title = QLabel()
        self.description = QLabel()
        # self.title.setStyleSheet("background-color: white")
        # self.description.setStyleSheet("background-color: white")
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        #self.setBackgroundRole(QtGui.QPalette.Dark)
        
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.rubberBandChanged.connect(self.onRubberBandChanged)
        self.last_rect = QtCore.QPointF()
        self.features = []
        self.main = main

    def setDescription(self):
        self.title.setText("Steps")
        self.title.setGeometry(QtCore.QRect(int(self.pixmap_item.pixmap().width())+18,20,500,50))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(50)
        self.title.setFont(font)
        self.scene().addWidget(self.title)
        # self.description.setStyleSheet("background-color:white")
        # self.title.setStyleSheet("background-color:white")
        self.description.adjustSize()
        self.description.setText("1)Drag and select the portion to be cropped from the socks image.\n2)After cropping the image choose the appropriate feature to be checked for the given cropped image.\n3)Save the feature and proceed similarly to select remaining features.\n4)Finally save all the features to the DB. ")
        self.description.setAlignment(QtCore.Qt.AlignLeft)
        self.description.setGeometry(QtCore.QRect(int(self.pixmap_item.pixmap().width())+20,90,1500,500))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.description.setFont(font)
        self.scene().addWidget(self.description)
    
    def saveAllFeatures(self):
        if not self.features == []:
            self.connect_db()
            self.main.close()

    def getModel(self,model):
        self.model = model    
    
    def getFileName(self,fileName):
        self.fileName = fileName

    def setPixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)

    def setButton(self):
        self.button.setGeometry(QtCore.QRect(10,int(self.pixmap_item.pixmap().height()) + 10,150,22))
        self.scene().addWidget(self.button)

    def zoomIn(self):
        self.scale(1.25, 1.25)

    def zoomOut(self):
        self.scale(0.8, 0.8)

    def resetZoom(self):
        self.resetTransform()

    def fitToWindow(self):
        self.fitInView(self.pixmap_item)

    @QtCore.pyqtSlot(QtCore.QRect, QtCore.QPointF, QtCore.QPointF)
    def onRubberBandChanged(self, rubberBandRect, fromScenePoint, toScenePoint):
        if rubberBandRect.isNull():
            pixmap = self.pixmap_item.pixmap()
            rect = self.pixmap_item.mapFromScene(self.last_rect).boundingRect().toRect()
            if not rect.intersected(pixmap.rect()).isNull():
                print(rect.x(),rect.y(),rect.right(), rect.bottom())
                self.x = rect.x()
                self.y = rect.y()
                self.right = rect.right()
                self.bottom = rect.bottom()
                self.width = rect.width()
                self.height = rect.height()
                crop_pixmap = pixmap.copy(rect)
                label = QtWidgets.QLabel(pixmap=crop_pixmap)
                _translate = QtCore.QCoreApplication.translate
                feature_type_label = QtWidgets.QLabel(text="Choose feature type")
                self.feature_type_combo_box = QtWidgets.QComboBox()
                self.feature_type_combo_box.addItem("Text")
                self.feature_type_combo_box.addItem("Image")
                self.feature_type_combo_box.addItem("RFID")
                push_button = QtWidgets.QPushButton("Add Feature")
                self.dialog = QtWidgets.QDialog(self)
                push_button.clicked.connect(self.add_feature)
                lay = QtWidgets.QVBoxLayout(self.dialog)
                lay.addWidget(label)
                lay.addWidget(feature_type_label)
                lay.addWidget(self.feature_type_combo_box)
                lay.addWidget(push_button)
                self.dialog.exec()
            self.last_rect = QtCore.QRectF()
        else:
            self.last_rect = QtCore.QRectF(fromScenePoint, toScenePoint)

    def add_feature(self):
        self.features.append(Feature(self.model,self.x,self.y,self.right,self.bottom,self.feature_type_combo_box.currentText()))
        self.dialog.close()
        m = self.pixmap_item.pixmap()
        p = QPainter(m)
        p.setPen(QPen(QtCore.Qt.red,2.5,QtCore.Qt.SolidLine))
        p.drawRect(QtCore.QRect(self.x,self.y,self.width, self.height))
        self.setPixmap(m)
        p.end()

    def create_connection(self,db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn


    def create_model(self,conn, model):
        sql = ''' INSERT INTO Models(id,x,y,right,bottom,feature)
                VALUES(?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, model)
        conn.commit()
         
    
    def connect_db(self):

        database = Constants.database_path

        
        sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS Models (
                                        id text NOT NULL,
                                        x text NOT NULL,
                                        y text NOT NULL,
                                        right text NOT NULL,
                                        bottom text NOT NULL,
                                        feature text NOT NULL
                                    );"""

        conn = self.create_connection(database)

        if conn is not None:
            self.create_table(conn, sql_create_projects_table)
            for i in range(len(self.features)):
                model = (self.features[i].modelId,self.features[i].x,self.features[i].y,self.features[i].right,self.features[i].bottom,self.features[i].feature_type)
                self.create_model(conn, model)
                self.saveImage()

        else:
            print("Error! cannot create the database connection.")


    def create_table(self,conn, create_table_sql):
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
                
class Feature:
    def __init__(self,modelId,x,y,right,bottom,feature_type):
        self.modelId = modelId
        self.x = x
        self.y = y
        self.right = right
        self.bottom = bottom
        self.feature_type = feature_type

class QImageViewer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        self.view = Viewer(self)
        self.setCentralWidget(self.view)

        self.printer = QtPrintSupport.QPrinter()

        self.createActions()
        self.createMenus()
        self.showMaximized()
    
    def setModel(self,model):
        self.model = model
        self.view.getModel(self.model)
        

    def open(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "Images (*.png *.jpeg *.jpg *.bmp *.gif)",
        )
        if fileName:
            self.view.setFileName(fileName)
            pixmap = QtGui.QPixmap(fileName)
            if pixmap.isNull():
                QtWidgets.QMessageBox.information(
                    self, "Image Viewer", "Cannot load %s." % fileName
                )
                return

            self.view.setPixmap(pixmap)
            self.view.setButton()
            self.view.setDescription()
            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                pass

    def print_(self):
        dialog = QtPrintSupport.QPrintDialog(self.printer, self)
        if dialog.exec_():
            pixmap = self.view.pixmap_item.pixmap()
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = pixmap.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            painter.drawPixmap(0, 0, pixmap)

    def fitToWindow(self):
        if self.fitToWindowAct.isChecked():
            self.view.fitToWindow()
        else:
            self.view.resetZoom()
        self.updateActions()

    def about(self):
        QtWidgets.QMessageBox.about(
            self,
            "About Image Viewer",
            "<p>The <b>Image Viewer</b> example shows how to combine "
            "QLabel and QScrollArea to display an image. QLabel is "
            "typically used for displaying text, but it can also display "
            "an image. QScrollArea provides a scrolling view around "
            "another widget. If the child widget exceeds the size of the "
            "frame, QScrollArea automatically provides scroll bars.</p>"
            "<p>The example demonstrates how QLabel's ability to scale "
            "its contents (QLabel.scaledContents), and QScrollArea's "
            "ability to automatically resize its contents "
            "(QScrollArea.widgetResizable), can be used to implement "
            "zooming and scaling features.</p>"
            "<p>In addition the example shows how to use QPainter to "
            "print an image.</p>",
        )

    def closeWindow(self):
        self.close()

    def createActions(self):
        self.openAct = QtWidgets.QAction(
            "&Open...", self, shortcut="Ctrl+O", triggered=self.open
        )
        self.printAct = QtWidgets.QAction(
            "&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_
        )
        self.exitAct = QtWidgets.QAction(
            "E&xit", self, shortcut="Ctrl+Q", triggered=self.close
        )
        self.zoomInAct = QtWidgets.QAction(
            "Zoom &In (25%)",
            self,
            shortcut="Ctrl++",
            enabled=False,
            triggered=self.view.zoomIn,
        )
        self.zoomOutAct = QtWidgets.QAction(
            "Zoom &Out (25%)",
            self,
            shortcut="Ctrl+-",
            enabled=False,
            triggered=self.view.zoomOut,
        )
        self.normalSizeAct = QtWidgets.QAction(
            "&Normal Size",
            self,
            shortcut="Ctrl+S",
            enabled=False,
            triggered=self.view.resetZoom,
        )
        self.fitToWindowAct = QtWidgets.QAction(
            "&Fit to Window",
            self,
            enabled=False,
            checkable=True,
            shortcut="Ctrl+F",
            triggered=self.fitToWindow,
        )

    def createMenus(self):

        self.fileMenu = QtWidgets.QMenu("&File / Capture", self)
 
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtWidgets.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())