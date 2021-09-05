from croppers import QImageViewer
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
from _sqlite3 import Error

class Ui_Form(object):
    def openWindow(self):

        if(self.textBox.text() != ''):
            self.window = QtWidgets.QMainWindow()
            Form.close()
            self.ui = QImageViewer()
            self.ui.show()
            self.ui.setWindowTitle("Image Viewer - "+self.textBox.text())
            self.ui.setModel(self.textBox.text())
            #connect_db()

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
        # self.comboBox = QtWidgets.QComboBox(Form)

        # self.comboBox.setObjectName("comboBox")
        # self.comboBox.addItem("")
        # self.comboBox.addItem("")
        # self.comboBox.addItem("")

        self.textBox = QtWidgets.QLineEdit(Form)
        self.textBox.setGeometry(QtCore.QRect(160, 240, 200, 22))
        # self.textBox.move(20, 20)
        # self.textBox.resize(280,40)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(170, 300, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.openWindow)
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 300, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(Form.close)
        
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Socks UI"))
        self.label.setText(_translate("Form", "Welcome"))
        self.label_2.setText(_translate("Form", "Provide Model Name and Proceed"))
        # self.comboBox.setItemText(0, _translate("Form", "Model 1"))
        # self.comboBox.setItemText(1, _translate("Form", "Model 2"))
        # self.comboBox.setItemText(2, _translate("Form", "Model 3"))
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
    
        