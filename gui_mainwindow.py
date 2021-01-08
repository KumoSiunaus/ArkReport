#coding: utf-8
import asyncio
import sys
import threading
import time

from PyQt5 import QtCore, QtWidgets

import core
from gui_simulator import simulator
from Ui_MainWindow import Ui_MainWindow


class Mainwindow(Ui_MainWindow, QtWidgets.QMainWindow):
    signal_simulator = QtCore.pyqtSignal(bool)
    signal_main = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.future_simulator = asyncio.Future()
        self.future_main = asyncio.Future()
        self.lock_simulator = threading.Lock()
        self.lock_main = threading.Lock()
        self.setupUi(self)

        self.switch_simulator = Switch(self.pushButton_simulator)
        self.switch_simulator.wait_text = "连接中"
        self.switch_simulator.on_text = "断开"
        self.switch_simulator.off_text = "连接"
        self.switch_simulator.aniwait.connect(
            lambda: self.label_simulator.setText("正在连接…"))
        self.switch_simulator.anion.connect(
            lambda: self.label_simulator.setText(simulator.name))
        self.switch_simulator.anioff.connect(
            lambda: self.label_simulator.setText("未连接"))

        self.signal_simulator.connect(self.called_by_simulator)
        self.signal_main.connect(self.called_by_main)

        def simulator_on() -> bool:
            with self.lock_simulator:
                self.switch_simulator._animation_wait()
                if simulator.connect():
                    self.switch_simulator._animation_on()
                    return True
                else:
                    self.switch_simulator._aninmation_off()
                    return False

        def simulator_off() -> bool:
            with self.lock_simulator:
                if self.switch_main.status:
                    main_off()
                if simulator.disconnect():
                    self.switch_simulator._aninmation_off()
                    return True
                else:
                    self.switch_simulator._animation_on()
                    return False

        self.switch_simulator.on.connect(simulator_on)
        self.switch_simulator.off.connect(simulator_off)

        self.switch_main = Switch(self.pushButton_main)
        self.switch_main.wait_text = "ArkReport --->--- 连接中"
        self.switch_main.on_text = "ArkReport ------- 已连接"
        self.switch_main.off_text = "ArkReport ---×--- 已断开"

        def main_on() -> bool:
            with self.lock_main:
                self.switch_main._animation_wait()
                if not self.switch_simulator.status:
                    if simulator_on():
                        self.future_main = asyncio.run_coroutine_threadsafe(
                            core.img_analyse(self.signal_main), core.loop)
                        self.switch_main._animation_on()
                        return True
                    else:
                        self.switch_main._aninmation_off()
                        return False
                else:
                    self.future_main = asyncio.run_coroutine_threadsafe(
                        core.img_analyse(self.signal_main), core.loop)
                    self.switch_main._animation_on()
                    return True

        def main_off() -> bool:
            with self.lock_main:
                self.future_main.cancel()
                self.switch_main._aninmation_off()
                return True

        self.switch_main.on.connect(main_on)
        self.switch_main.off.connect(main_off)

        self.isClosed = True
        self.pushButton_simulator.clicked.connect(self.switch_simulator.click)
        self.pushButton_main.clicked.connect(self.switch_main.click)
        self.pushButton_penguin.clicked.connect(self.changeid)

    def called(self, *args, **kwargs):

        PenguinID = kwargs["PenguinID"]
        if not PenguinID == "":
            self.label_penguin.setText(f"#{PenguinID}")
        else:
            self.label_penguin.setText("未登录")
        self.show()
        QtWidgets.QApplication.processEvents()
        self.future_simulator = asyncio.run_coroutine_threadsafe(
            simulator.listen(self.signal_simulator), core.loop)

    def called_by_simulator(self, res: bool):
        if self.lock_simulator.locked():
            return
        with self.lock_simulator:
            if not self.switch_simulator.status == res:
                if res:
                    self.switch_simulator._animation_on()
                else:
                    self.switch_simulator._aninmation_off()
                    if not simulator.get_serial():
                        self.label_simulator.setText("正在搜索…")
                        self.pushButton_simulator.setEnabled(False)
                        self.pushButton_simulator.setText("搜索中")

    def called_by_main(self, res: str):
        self.textBrowser.append(res)

    def changeid(self):
        self.hide()
        self.parent.call(self.parent.loginwin, "changeid")

        self.future_simulator.cancel()


class Switch(QtCore.QObject):
    '''
    Switch(button: QpushButton)\n
    Set a QPushButton object as a switch\n
    '''
    aniwait = QtCore.pyqtSignal()
    anion = QtCore.pyqtSignal()
    anioff = QtCore.pyqtSignal()
    on = QtCore.pyqtSignal()
    off = QtCore.pyqtSignal()

    def __init__(self, button: QtWidgets.QPushButton) -> None:
        super().__init__()
        self.button = button
        self.status = self.button.isChecked()
        self.wait_text = "WAIT"
        self.on_text = "ON"
        self.off_text = "OFF"

    def _animation_wait(self):  # ONLY Chage the animation
        self.button.setEnabled(False)
        self.button.setText(self.wait_text)
        self.aniwait.emit()
        QtWidgets.QApplication.processEvents()

    def _animation_on(self):  # ONLY Chage the animation
        self.button.setEnabled(True)
        self.button.setChecked(True)
        self.button.setText(self.on_text)
        self.anion.emit()
        QtWidgets.QApplication.processEvents()
        self.status = True

    def _aninmation_off(self):  # ONLY Chage the animation
        self.button.setEnabled(True)
        self.button.setChecked(False)
        self.button.setText(self.off_text)
        self.anioff.emit()
        QtWidgets.QApplication.processEvents()
        self.status = False

    def __on(self) -> bool:
        self.on.emit()

    def __off(self) -> bool:
        self.off.emit()

    def click(self):
        status = self.status
        if not status:
            self.__on()
        else:
            self.__off()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator()
    translator.load("qt_zh_CN.qm")
    app.installTranslator(translator)
    window = Mainwindow()
    window.show()
    window.test()
    app.exec_()
