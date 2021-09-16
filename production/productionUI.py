from constants import Constants
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
from _sqlite3 import Error
from check import QImageViewers

class Ui_Form(object):
    def openWindow(self):
        self.window =QtWidgets.QMainWindow()
        Form.close()
        self.ui = QImageViewers()
        self.ui.show()
        self.ui.setWindowTitle("Image Viewer - "+self.comboBox.currentText())
        self.ui.setModel(self.comboBox.currentText())

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(564, 435)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(150, 70, 241, 61))
        font = QtGui.QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(120, 190, 300, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setGeometry(QtCore.QRect(150, 240, 200, 22))
        self.comboBox.setObjectName("comboBox")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(170, 300, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 300, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton.clicked.connect(self.openWindow)
        self.pushButton_2.clicked.connect(Form.close)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def create_connection(self,db_file):
            conn = None
            try:
                conn = sqlite3.connect(db_file)
            except Error as e:
                print(e)
            return conn

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Welcome"))
        self.label_2.setText(_translate("Form", "Choose a Master Model"))
        database = Constants.database_path
        conn = self.create_connection(database)
        if conn is not None:
        # create projects table
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT id FROM Models")
            rows = cursor.fetchall()
            for row in rows:
                self.comboBox.addItem(row[0])
        else:
            print("Error! cannot create the database connection.")
        # create a new project
        # what diff da
        
        
        self.pushButton.setText(_translate("Form", "OK"))
        self.pushButton_2.setText(_translate("Form", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())