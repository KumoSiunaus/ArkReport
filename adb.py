import os
import subprocess
import sys

import cv2
import numpy


class ADB:

    _adb_path = r"adb\adb"
    _serial = ""

    def connect(self, serial="127.0.0.1:5555"):

        os.system("cls")
        print("正在连接模拟器...", end="", flush=True)

        self._serial = serial
        output = subprocess.check_output(
            f"{self._adb_path} connect {self._serial}")
        output = output.decode("utf-8")

        if f"connected to {serial}" in output:
            return True
        else:
            return False

    def disconnect(self):

        subprocess.call(f"{self._adb_path} disconnect {self._serial}")

    def get_size(self) -> str:

        output = subprocess.check_output(f"{self._adb_path} shell wm size")
        output = output.decode("utf-8")

        return output.rstrip()

    def screenshot(self):

        with subprocess.Popen(f"{self._adb_path} exec-out screencap -p",
                              stdout=subprocess.PIPE) as p:
            output = p.communicate()[0]

            img = cv2.imdecode(numpy.frombuffer(output, numpy.uint8),
                               cv2.IMREAD_COLOR)
            return img

    def swipe(self, pos1, pos2):

        subprocess.call(
            f"{self._adb_path} shell input swipe {pos1[0]} {pos1[1]} {pos2[0]} {pos2[1]}"
        )
