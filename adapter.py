#coding: utf-8
import ctypes
import ctypes.wintypes
import json
import os
import sys

import pyautogui
from adb import ADB
from win32 import win32api, win32gui
from win32.lib import win32con

label = "CN"

_hwnd_title = {}


def _get_all_hwnd(hwnd, mouse):

    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(
            hwnd) and win32gui.IsWindowVisible(hwnd):
        if win32gui.GetWindowText(hwnd) != "":
            _hwnd_title.update({win32gui.GetWindowText(hwnd): hwnd})


win32gui.EnumWindows(_get_all_hwnd, 0)


def _get_child_windows(hwnd):

    if not hwnd:
        return
    childhwnd_list = []
    win32gui.EnumChildWindows(hwnd, lambda hwnd, param: param.append(hwnd),
                              childhwnd_list)
    return childhwnd_list


def _get_window_pos(hwnd):

    pos = win32gui.GetWindowRect(hwnd)
    return (pos[1], pos[3], pos[0], pos[2])


def focus(hwnd):
    user32 = ctypes.WinDLL("user32")
    if user32.IsIconic(hwnd):
        win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE,
                             0)
    win32api.keybd_event(0, 0, 0, 0)
    win32gui.SetForegroundWindow(hwnd)


class _Window():
    def set_pos(self, pos: tuple):

        self.top = pos[0]
        self.bottom = pos[1]
        self.left = pos[2]
        self.right = pos[3]
        self.centre = ((self.top + self.bottom) // 2,
                       (self.left + self.right) // 2)
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def set_size(self, size: tuple):

        self.width = int(size[0])
        self.height = int(size[1])


class _Block:
    def set_pos_by_per(self, pos_per: tuple, inner_window):

        self.top = round(pos_per[0] * inner_window.height)
        self.bottom = round(pos_per[1] * inner_window.height)
        self.left = round(pos_per[2] * inner_window.width)
        self.right = round(pos_per[3] * inner_window.width)
        self.centre = ((self.top + self.bottom) // 2,
                       (self.left + self.right) // 2)
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def set_size_by_per(self, size_per: tuple, inner_window):

        self.width = round(size_per[0] * inner_window.width)
        self.height = round(size_per[1] * inner_window.height)


class _Button(_Block):
    def set_pos_by_per(self, pos_per: tuple, inner_window):

        self.top = round(pos_per[0] * inner_window.height)
        self.bottom = round(pos_per[1] * inner_window.height)
        self.left = round(pos_per[2] * inner_window.width)
        self.right = round(pos_per[3] * inner_window.width)
        self.centre = ((self.top + self.bottom) // 2,
                       (self.left + self.right) // 2)
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def press(self, hwnd):

        adapt()
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0,
                             (self.centre[0] + top_blank) * 65536 +
                             (self.centre[1]) + left_blank)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0,
                             (self.centre[0] + top_blank) * 65536 +
                             (self.centre[1]) + left_blank)


def _get_blank(window1, window2):

    global top_blank, left_blank
    top_blank = abs(window1.top - window2.top)
    left_blank = abs(window1.left - window2.left)
    return top_blank, left_blank


def adapt():

    _hwnd_win.set_pos(_get_window_pos(hwnd))
    _childhwnd_win.set_pos(_get_window_pos(childhwnd))
    top_blank, left_blank = _get_blank(_hwnd_win, _childhwnd_win)

    stage.set_pos_by_per((660 / 1080, 784 / 1080, 0 / 2160, 249 / 2160),
                         simulator_win)
    end.set_pos_by_per((868 / 1080, 1013 / 1080, 50 / 2160, 601 / 2160),
                       simulator_win)
    baseline_h.set_pos_by_per(
        (1006 / 1080, 1007 / 1080, 0 / 2160, 2160 / 2160), simulator_win)
    baseline_v.set_pos_by_per(
        (690 / 1080, 1037 / 1080, 661 / 2160, 663 / 2160), simulator_win)
    quantity.set_pos_by_per((93 / 1080, 134 / 1080, 73 / 2160, 124 / 2160),
                            simulator_win)
    type_name.set_size_by_per((0, 30 / 1080), simulator_win)
    drop.set_size_by_per((220 / 2160, 235 / 1080), simulator_win)

    esc.set_pos_by_per((20 / 1080, 95 / 1080, 24 / 2160, 243 / 2160),
                       _childhwnd_win)


with open("resource/simulator.json", encoding="utf-8") as f:
    simulator = json.loads(f.read())

hwnd = 0
for simulator_, port_ in simulator.items():
    for title_ in _hwnd_title:
        if simulator_ in title_:
            hwnd = _hwnd_title[title_]
            title = title_
            port = port_

childhwnd_list = _get_child_windows(hwnd)
childhwnd = 0
for hwnd_ in childhwnd_list:
    pos = _get_window_pos(hwnd_)
    width = pos[3] - pos[2]
    height = pos[1] - pos[0]
    if height * 2 == width:
        childhwnd = hwnd_

if hwnd == 0 or childhwnd == 0:
    #os.system("cls")
    print("未找到正在运行的模拟器程序。")
    print("这可能是因为：")
    print("1) 模拟器分辨率设置不正确：请调整分辨率比例为2:1（如2160*1080）")
    print("2) 模拟器未加入列表：请提交issue告知我们模拟器的窗口名称")
    sys.exit(0)

device = ADB()
host = "127.0.0.1"
if not device.connect(serial=f"{host}:{port}"):
    #os.system("cls")
    print("已找到模拟器程序，但模拟器连接失败。")
    print("这可能是因为：")
    print("1) 模拟器的端口不正确：请提交issue向我们反馈")
    print("2) 其他未知的原因（如adb相关问题）：请提交issue详细说明")
else:
    print("OK")

_simulator_size = device.get_size().split(": ")[1]
simulator_win = _Window()
simulator_win.set_size(tuple(_simulator_size.split("x")))

_hwnd_win = _Window()
_childhwnd_win = _Window()
top_blank = 0
left_blank = 0

end = _Block()
stage = _Block()
baseline_h = _Block()
baseline_v = _Block()
quantity = _Block()
type_name = _Block()
drop = _Block()

esc = _Button()
