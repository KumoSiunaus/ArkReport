#coding: utf-8

import ctypes
import sys

import cv2
import numpy
from cnocr import CnOcr
from PyQt5.QtWidgets import QApplication
from win32 import win32gui

from adapter import *

_ocr = CnOcr()


def get_image():

    adapt()
    img = device.screenshot()
    return img


def get_drop_type(img):
    def count_pixel(row: list):
        pixel = 0
        for pix in row:
            if pix == 255:
                pixel += 1
        return pixel

    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_bin = cv2.threshold(img_grey[baseline_h.top:baseline_h.bottom, :],
                                 60, 255, cv2.THRESH_BINARY)

    pix_max = 0
    for row in img_bin:
        if count_pixel(row[baseline_v.right + 30:]) > pix_max:
            pix_max = count_pixel(row)
            baseline_horizontal = row

    isover = 0
    drop_type_range_temp = [0, 0]
    drop_type_range = []
    for pix in range(baseline_v.right + 30, baseline_h.right):
        if baseline_horizontal[pix] != baseline_horizontal[pix - 1]:
            drop_type_range_temp[isover % 2] = pix
            if isover is True:
                if drop_type_range_temp[1] - drop_type_range_temp[
                        0] >= drop.width:
                    drop_type_range.append(tuple(drop_type_range_temp))
            isover = not isover

    drop_type = {}
    for type_range in drop_type_range:
        type_img = img[baseline_h.bottom + 1:baseline_h.bottom +
                       type_name.height, type_range[0]:type_range[1]]
        text = find_text(type_img, 90)
        if text == "常规掉落": drop_type["NORMAL_DROP"] = type_range
        if text == "特殊掉落": drop_type["SPECIAL_DROP"] = type_range
        if text == "额外物资": drop_type["EXTRA_DROP"] = type_range
        if text == "幸运掉落": drop_type["FURNITURE"] = type_range

    return drop_type


def get_drop_image(img, drop_type):

    drop_img = {}
    for type_, range_ in drop_type.items():
        drop_count = round((range_[1] - range_[0]) / drop.width)
        if drop_count == 0: lenth = 0
        else:
            lenth = (range_[1] - range_[0]) // drop_count
        drop_img[type_] = []
        for i in range(drop_count):
            drop_img[type_].append(
                img[baseline_h.top - drop.height:baseline_h.top - 1,
                    range_[0] + i * lenth:range_[0] + (i + 1) * lenth])

    return drop_img


def get_quantity_image(drop_img, loc: tuple):

    top = loc[1] + quantity.top
    bottom = loc[1] + quantity.bottom
    left = loc[0] + quantity.left
    right = loc[0] + quantity.right

    quantity_image = drop_img[top:bottom, left:right]
    return quantity_image


def get_stage_image(img):

    img_stage = img[stage.top:stage.bottom, stage.left:stage.right]
    return img_stage


def find_image(img, templ, loc):

    if img == []:
        loc.clear()
        loc.extend([-1, -1])
        return 0
    item_img_adapted = cv2.resize(templ, (0, 0),
                                  fx=simulator_win.width / 1882,
                                  fy=simulator_win.height / 941)
    res = cv2.matchTemplate(img, item_img_adapted, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    loc.clear()
    loc.extend(list(max_loc))

    return max_val


def find_quantity(img):

    ret, img_bin = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY_INV)
    _ocr.set_cand_alphabet("0123456789")
    res = _ocr.ocr_for_single_line(img_bin)
    resstr = ("".join(res))

    resstr = resstr.replace(" ", "")
    return resstr


def find_text(img, threshold):

    ret, img_bin = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY_INV)
    _ocr.set_cand_alphabet(None)
    res = (_ocr.ocr_for_single_line(img_bin))
    resstr = ("".join(res))

    resstr = resstr.replace(" ", "")
    return resstr


def find_stage(img):

    ret, img_bin = cv2.threshold(img, 254, 255, cv2.THRESH_BINARY_INV)
    _ocr.set_cand_alphabet("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-")
    res = (_ocr.ocr_for_single_line(img_bin))
    resstr = ("".join(res))

    resstr = resstr.replace(" ", "")
    return resstr


def QImage_to_mat(img):

    ptr = img.constBits()
    ptr.setsize(img.byteCount())

    mat = numpy.array(ptr).reshape(img.height(), img.width(), 4)
    return mat
