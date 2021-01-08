import asyncio
import json
import subprocess

import cv2
import numpy
import win32gui


class Simulator:
    def __init__(self):
        self.adb_path = r"adb\adb"
        self.name = ""
        self.hwnd = 0
        self.host = ""
        self.port = 0
        self.serial = ""

    def get_serial(self) -> bool:
        hwnd_title = {}

        def get_all_hwnd(hwnd, mouse):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(
                    hwnd) and win32gui.IsWindowVisible(hwnd):
                if win32gui.GetWindowText(hwnd) != "":
                    hwnd_title.update({win32gui.GetWindowText(hwnd): hwnd})

        win32gui.EnumWindows(get_all_hwnd, 0)

        with open("resource/simulator.json", encoding="utf-8") as f:
            simulators: dict = json.loads(f.read())
        for simulator, port in simulators.items():
            for title in hwnd_title:
                if simulator in title:
                    self.name = simulator
                    self.hwnd = hwnd_title[title]
                    self.host = "127.0.0.1"
                    self.port = port
                    self.serial = f"{self.host}:{self.port}"
                    self.connect()
                    return True
        self.__init__()
        return False

    async def start_server(self) -> None:
        await asyncio.create_subprocess_shell(f"{self.adb_path} start-server",
                                              stdout=subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)

    def isconnected(self) -> bool:
        devices = self.devices()
        if self.serial in devices:
            if devices[self.serial] == "device":
                return True
        return False

    def connect(self) -> bool:
        subprocess.call(f"{self.adb_path} connect {self.serial}",
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        devices = self.devices()
        if self.serial in devices:
            if devices[self.serial] == "device":
                return True
        return False

    def disconnect(self) -> bool:
        subprocess.call(f"{self.adb_path} disconnect {self.serial}",
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        devices = self.devices()
        if not self.serial in devices:
            return True
        elif not devices[self.serial] == "device":
            return True
        else:
            return False

    async def listen(self, signal):
        while True:
            while not self.get_serial():
                await asyncio.sleep(1)
            else:
                while not self.serial == "":
                    signal.emit(self.isconnected())
                    await asyncio.sleep(1)

    def devices(self) -> dict:
        devices = {}
        p = subprocess.Popen(f"{self.adb_path} devices",
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        stdout, stderr = p.communicate()
        stdout = stdout.decode("utf-8").rstrip()
        device_list = list(filter(lambda x: "\t" in x, stdout.split("\r\n")))
        for device in device_list:
            devices.update({device.split("\t")[0]: device.split("\t")[1]})
        return devices

    async def get_size(self) -> str:

        output = subprocess.check_output(f"{self.adb_path} shell wm size")
        output = output.decode("utf-8")

        return output.rstrip()

    async def screenshot(self):
        p = await asyncio.create_subprocess_shell(
            f"{self.adb_path} exec-out screencap -p",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL)
        stdout, stderr = await p.communicate()
        img = cv2.imdecode(numpy.frombuffer(stdout, numpy.uint8),
                           cv2.IMREAD_COLOR)
        return img

    def swipe(self, pos1, pos2):
        subprocess.call(
            f"{self.adb_path} shell input swipe {pos1[0]} {pos1[1]} {pos2[0]} {pos2[1]}"
        )

    def click(self, pos):
        subprocess.call(f"{self.adb_path} shell input tap {pos[0]} {pos[1]}")


# if __name__ == "__main__":

simulator = Simulator()
