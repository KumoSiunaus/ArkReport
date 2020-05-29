# -*- coding: utf-8 -*-

import ctypes
import sys

import cv2
from PyQt5.QtWidgets import QApplication
from win32 import win32gui

import find
from QImage2Mat import QImage2Mat
from resolution import *


def image(hwnd):
    adapt()
    user32 = ctypes.WinDLL("user32")
    if user32.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, 3)
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    img_Q = screen.grabWindow(hwnd).toImage()
    img = cv2.cvtColor(QImage2Mat(img_Q), cv2.COLOR_BGRA2BGR)

    return img


def droptype(img):

    def countpix(row: list):
        pix_count = 0
        for pix in row:
            if pix == 255:
                pix_count += 1
        return pix_count

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_bin = cv2.threshold(
        img[horiz.top: horiz.bottom, :], 60, 255, cv2.THRESH_BINARY)

    pix_max = 0
    for row in img_bin:
        if countpix(row[vert.right + 30:]) > pix_max:
            pix_max = countpix(row)
            typeline = row

    s = 0
    temp = [0, 0]
    typeline_split = []
    for i in range(vert.right + 30, horiz.right):
        if typeline[i] != typeline[i - 1]:
            temp[s % 2] = i
            if s % 2 == 1:
                if temp[1] - temp[0] > type_single.width:
                    typeline_split.append(tuple(temp))
            s += 1

    droptype = {}
    for typerange in typeline_split:
        typeimg = img[horiz.bottom + 1: horiz.bottom +
                      type_single.height, typerange[0]: typerange[1]]
        text = find.text(typeimg, 90)
        if text == "常规掉落":
            droptype["NORMAL_DROP"] = typerange
        if text == "特殊掉落":
            droptype["SPECIAL_DROP"] = typerange
        if text == "额外物资":
            droptype["EXTRA_DROP"] = typerange
        if text == "幸运掉落":
            droptype["FURNITURE"] = typerange

    return droptype


def dropimg(img, droptype):
    dropimg = {}
    for k, v in droptype.items():
        n = round((v[1] - v[0]) / type_single.width)
        if n == 0:
            lenth = 0
        else:
            lenth = (v[1] - v[0]) // n
        dropimg[k] = []
        for i in range(n):
            dropimg[k].append(
                img[horiz.top - drop.height: horiz.top - 1, v[0] + i * lenth: v[0] + (i + 1) * lenth])

    return dropimg


def quantityimg(dropimg, loc: tuple):

    top = loc[1] + quant.top
    bottom = loc[1] + quant.bottom
    left = loc[0] + quant.left
    right = loc[0] + quant.right

    img_c = dropimg[top:bottom, left:right]
    return img_c


def stageimg(img):
    img_stage = img[stage.top:stage.bottom, stage.left:stage.right]
    return img_stage
