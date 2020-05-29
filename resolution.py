# -*- coding: utf-8 -*-

import sys
import ctypes.wintypes
from win32 import win32gui, win32api
from win32.lib import win32con

hwnd_title = {}


def get_all_hwnd(hwnd, mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
        if win32gui.GetWindowText(hwnd) != "":
            hwnd_title.update({win32gui.GetWindowText(hwnd): hwnd})


win32gui.EnumWindows(get_all_hwnd, 0)


def get_child_windows(hwnd):
    if not hwnd:
        return
    hwndChildList = []
    win32gui.EnumChildWindows(
        hwnd, lambda hwnd, param: param.append(hwnd),  hwndChildList)
    return hwndChildList


def get_window_pos(hwnd):
    pos = win32gui.GetWindowRect(hwnd)
    return (pos[1], pos[3], pos[0], pos[2])


class block:
    def set_pos(self, pos: tuple):
        self.top = pos[0]
        self.bottom = pos[1]
        self.left = pos[2]
        self.right = pos[3]
        self.centre = ((self.top + self.bottom) // 2,
                       (self.left + self.right) // 2)
        self.height = self.bottom - self.top
        self.width = self.right - self.left

    def set_pos_per(self, pos_per: tuple, inframe_size, outframe_size):
        top_blank = abs(outframe_size.top - inframe_size.top)
        left_blank = abs(outframe_size.left - inframe_size.left)
        self.top = round(pos_per[0] * inframe_size.height) + top_blank
        self.bottom = round(pos_per[1] * inframe_size.height) + top_blank
        self.left = round(pos_per[2] * inframe_size.width) + left_blank
        self.right = round(pos_per[3] * inframe_size.width) + left_blank
        self.centre = ((self.top + self.bottom) // 2,
                       (self.left + self.right) // 2)
        self.height = self.bottom - self.top
        self.width = self.right - self.left

    def set_size_per(self, size_per: tuple, inframe_size):
        self.width = round(size_per[0] * inframe_size.width)
        self.height = round(size_per[1] * inframe_size.height)

    def press(self, hwnd):
        adapt()
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                             0, self.centre[0]*65536 + self.centre[1])
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP,
                             0, self.centre[0]*65536 + self.centre[1])


def adapt():
    hwnd_size.set_pos(get_window_pos(hwnd))
    childhwnd_size.set_pos(get_window_pos(childhwnd))

    check.set_pos_per((819/941, 900/941, 1566/1882, 1835/1882),
                      childhwnd_size, hwnd_size)
    start.set_pos_per((479/941, 844/941, 1458/1882, 1634/1882),
                      childhwnd_size, hwnd_size)
    esc.set_pos_per((17/941, 82/941, 21/1882, 210/1882),
                    childhwnd_size, hwnd_size)
    stage.set_pos_per((611/941, 685/941, 23/1882, 225/1882),
                      childhwnd_size, hwnd_size)
    end.set_pos_per((755/941, 885/941, 42/1882, 526/1882),
                    childhwnd_size, hwnd_size)
    yes.set_pos_per((723/941, 780/941, 1500/1882, 1556/1882),
                    childhwnd_size, hwnd_size)
    no.set_pos_per((725/941, 783/941, 42/1882, 1152/1882),
                   childhwnd_size, hwnd_size)
    horiz.set_pos_per((875/941, 879/941, 0/1882, 1882/1882),
                      childhwnd_size, hwnd_size)
    vert.set_pos_per((601/941, 904/941, 576/1882, 578/1882),
                     childhwnd_size, hwnd_size)
    quant.set_pos_per((81/941, 117/941, 64/1882, 108/1882),
                      childhwnd_size, childhwnd_size)
    type_single.set_size_per((190/1882, 30/941), childhwnd_size)
    drop.set_size_per((0, 200/941), childhwnd_size)


label = "CN"

with open("simulator.txt", encoding="utf-8") as f:
    simulator = f.readlines()
    for i, v in enumerate(simulator):
        simulator[i] = simulator[i].strip("\n")

hwnd = 0
for s in simulator:
    for t in hwnd_title:
        if s in t:
            hwnd = hwnd_title[t]

if hwnd == 0:
    print("未找到正在运行的模拟器程序。")
    print("这可能是因为：")
    print("1) 模拟器分辨率设置不正确：请调整分辨率比例为2:1（如2160*1080）")
    print("2) 模拟器未加入列表：请将窗口标题内的模拟器名称写入simulator.txt文件内")
    sys.exit(0)

childhwndList = get_child_windows(hwnd)

for h in childhwndList:
    pos = get_window_pos(h)
    width = pos[3] - pos[2]
    height = pos[1] - pos[0]
    if height * 2 == width:
        childhwnd = h

hwnd_size = block()
childhwnd_size = block()
check = block()
start = block()
esc = block()
stage = block()
end = block()
yes = block()
no = block()
horiz = block()
vert = block()
quant = block()
type_single = block()
drop = block()
