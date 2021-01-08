#coding: utf-8

import os
import sys
import penguin

from PyQt5 import QtCore, QtWidgets

from Ui_LoginWindow import Ui_LoginWindow


class LoginWindow(Ui_LoginWindow, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window
                            | QtCore.Qt.WindowMinimizeButtonHint
                            | QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.button_ok = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.button_cancel = self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Cancel)
        self.lineEdit.returnPressed.connect(self.button_ok.click)
        self.button_ok.setText("登录")
        self.button_cancel.setText("退出")
        self.button_ok.clicked.connect(self.login)
        self.button_cancel.clicked.connect(sys.exit)
        self.button_ok.setAutoDefault(True)
        self.button_cancel.setAutoDefault(True)
        self.label_idnotexist.setVisible(False)
        self.lineEdit.setText(self.check_log())
        self.lineEdit.setFocus()

    def called(self, *args, **kwargs):
        if "changeid" in args:
            self.lineEdit.setFocus()
            self.lineEdit.selectAll()

        self.show()
        QtWidgets.QApplication.processEvents()

    def check_log(self):
        if os.path.exists("PenguinID.dat"):
            with open("PenguinID.dat") as f:
                return f.read()
        else:
            return ""

    def login(self) -> str:
        self.hide()
        PenguinID = self.lineEdit.text()
        res = penguin.login(PenguinID)
        if res == "accepted" or res == "blank":
            self.label_idnotexist.hide()
            self.parent.call(self.parent.mainwin, PenguinID=PenguinID)
        elif res == "rejected":
            self.label_idnotexist.show()
            self.lineEdit.setFocus()
            self.lineEdit.selectAll()
            self.show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).click()

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator()
    translator.load("qt_zh_CN.qm")
    app.installTranslator(translator)
    window = LoginWindow()
    window.show()
    app.exec_()
