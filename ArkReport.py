# coding: utf-8
import asyncio
import sys

from PyQt5 import QtCore, QtWidgets

import core
from gui_loginwindow import LoginWindow
from gui_mainwindow import Mainwindow
from gui_simulator import simulator


class Ark:
    def __init__(self, app: QtWidgets.QApplication):
        self.app = app
        self.windows = WinControl(self)

        self.start()

    def start(self) -> None:
        async def exec_():
            core.set_threading()
            self.windows.call(self.windows.loginwin)
            await simulator.start_server()

        asyncio.run(exec_())
        self.app.exec()


class WinControl:
    def __init__(self, parent: Ark) -> None:
        self.parent = parent
        self.loginwin = LoginWindow(self)
        self.mainwin = Mainwindow(self)

    @staticmethod
    def call(obj, *args, **kwargs) -> None:
        obj.called(*args, **kwargs)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator()
    translator.load("qt_zh_CN.qm")
    app.installTranslator(translator)
    ark = Ark(app)
