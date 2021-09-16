from constants import Constants
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
import sqlite3

import cv2
from numpy import random
from main import ProductionSet
from yolo_object_detection_webcam import yoloDetectionModel
from _sqlite3 import Error
from PyQt5.QtGui import QColor, QPainter, QPalette, QPen
from PyQt5.QtWidgets import  QLabel, QLabel

class Viewer(QtWidgets.QGraphicsView):
    def __init__(self,main, parent=None):
        super().__init__(QtWidgets.QGraphicsScene(), parent)
        self.pixmap_item = self.scene().addPixmap(QtGui.QPixmap())
        self.button = QtWidgets.QPushButton("Save All Features")
        self.title = QLabel()
        self.description = QLabel()
        self.finalResult = QLabel()
        #self.title.setStyleSheet("background-color: white")
        #self.description.setStyleSheet("background-color: white")
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        #self.setBackgroundRole(QtGui.QPalette.Dark)
        
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.rubberBandChanged.connect(self.onRubberBandChanged)
        self.last_rect = QtCore.QPointF()
        self.features = []
        self.main = main

    def setDescription(self):
        self.title.setText("Result")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setGeometry(QtCore.QRect(int(self.pixmap_item.pixmap().width())+100,20,800,50))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(50)
        self.title.setFont(font)
        self.scene().addWidget(self.title)
        self.description.setStyleSheet("background-color:white")
        self.title.setStyleSheet("background-color:white")
        self.description.adjustSize()
        self.description.setAlignment(QtCore.Qt.AlignCenter)
        self.description.setGeometry(QtCore.QRect(int(self.pixmap_item.pixmap().width())+120,90,800,300))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.description.setFont(font)
        self.scene().addWidget(self.description)


    def setFinalResult(self):
        font = QtGui.QFont()
        font.setPointSize(50)
        font.setBold(True)
        font.setWeight(100)
        # self.finalResult.setStyleSheet("background-color:white")
        self.finalResult.adjustSize()
        self.finalResult.setAlignment(QtCore.Qt.AlignCenter)
        self.finalResult.setGeometry(QtCore.QRect(int(self.pixmap_item.pixmap().width())+120,self.description.height() + 60,800,300))
        self.finalResult.setFont(font)
        
        self.scene().addWidget(self.finalResult)

    def setPixmap(self, pixmap, fileName, crop_coor):
        self.crop_coor = crop_coor
        self.fileName = fileName
        self.pixmap_item.setPixmap(pixmap)
        self.startTest()


    def startTest(self):
        self.connect_db()
        if(any(isinstance(sub,list) for sub in self.pts)):
            for i in range(len(self.pts)):
                self.drawRectangle(self.pts[i],QtCore.Qt.green)
            
        else:
            self.drawRectangle(self.pts,QtCore.Qt.red)

    def drawRectangle(self,pts,color):

        print(pts)
        m = self.pixmap_item.pixmap()
        p = QPainter(m)
        p.setPen(QPen(color,2.5,QtCore.Qt.SolidLine))
        p.drawRect(QtCore.QRect(pts[0],pts[1],pts[2]-pts[0],pts[3]-pts[1]))
        self.pixmap_item.setPixmap(m)
        p.end()
        

    def getModel(self,model):
        self.model = model
        print(self.model)  

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
                self.dialog = QtWidgets.QDialog(self)
                lay = QtWidgets.QVBoxLayout(self.dialog)
                lay.addWidget(label)
                self.dialog.exec()
            self.last_rect = QtCore.QRectF()
        else:
            self.last_rect = QtCore.QRectF(fromScenePoint, toScenePoint)

    def create_connection(self,db_file):
        """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
        print("yes")
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn


    def create_model(self,conn, model):
        """
        Create a new project into the projects table
        :param conn:
        :param project:
        :return: project id
        """
        sql = ''' INSERT INTO Models(id,x,y,right,bottom,feature)
                VALUES(?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, model)
        conn.commit()
        print("yes")
         
    
    def connect_db(self):
        database = Constants.database_path
        
        query = "SELECT * FROM Models WHERE id = '"+self.model+"'"; 

    # create a database connection
        conn = self.create_connection(database)

    # create tables
        if conn is not None:
        # create projects table
        # model = (self.model,self.x,self.y,self.right,self.bottom,self.feature_type_combo_box.currentText())
            try:
                c = conn.cursor()
                c.execute(query)
                rows = c.fetchall()
                feature_pts = []
                feature_types = []
                for row in rows:
                    print(row)
                    feature_pts.append([int(row[1]),int(row[2]),int(row[3]),int(row[4])])
                    feature_types.append(row[5])
                self.feature_pts = feature_pts
                print(feature_pts)
                print(feature_types)
                obj = ProductionSet(feature_pts,feature_types,self.fileName,self.model)
                self.pts = obj.checkAllFeatures()
                result = ''
                for featureName,featureResult in obj.result.items():
                    result += featureName+" : "+featureResult+"\n"
                self.description.setText(result)
                if(any(isinstance(sub,list) for sub in self.pts)):
                    print("VALID CARD !")
                    self.finalResult.setStyleSheet("background-color:white;color: rgb(0,128,0)")
                    self.finalResult.setText(" VALID CARD ! ")
                else:
                    self.finalResult.setStyleSheet("background-color:white;color: rgb(255,0,0)")
                    self.finalResult.setText(" INVALID CARD ! ")


            except Error as e:
                print(e)
        else:
            print("Error! cannot create the database connection.")
        # create a new project

class QImageViewers(QtWidgets.QMainWindow):
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
        print(self.model)  


    def open(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "Images (*.png *.jpeg *.jpg *.bmp *.gif)",
        )
        if fileName:
            model = yoloDetectionModel(fileName)
            crop_coordinates = model.crop_coor_func()
            img = cv2.imread(fileName)
            # img = cv2.resize(img, None, fx=0.7, fy=0.7)
            img = img[crop_coordinates[1]:crop_coordinates[3],crop_coordinates[0]:crop_coordinates[2]]
            rand = random.randint(50)
            cv2.imwrite(f"{Constants.iteration_test_images}{rand}.jpg",img)
            fileName = f"{Constants.iteration_test_images}{rand}.jpg"
            pixmap = QtGui.QPixmap(fileName)
            if pixmap.isNull():
                QtWidgets.QMessageBox.information(
                    self, "Image Viewer", "Cannot load %s." % fileName
                )
                return

            
            self.view.setPixmap(pixmap,fileName,crop_coordinates)
            self.view.setDescription()
            self.view.setFinalResult()
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
    imageViewer = QImageViewers()
    imageViewer.show()
    sys.exit(app.exec_())