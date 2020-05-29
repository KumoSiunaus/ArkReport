# -*- coding: utf-8 -*-

import cv2
from cnocr import ENG_LETTERS, NUMBERS, CnOcr

from resolution import childhwnd_size

ocr = CnOcr()


def image(img, itemimg, loc):
    if img == []:
        loc.clear()
        loc.extend([-1, -1])
        return 0
    itemimg_adapted = cv2.resize(
        itemimg, (0, 0), fx=childhwnd_size.width/1882, fy=childhwnd_size.height/941)
    res = cv2.matchTemplate(img, itemimg_adapted, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    loc.clear()
    loc.extend(list(max_loc))
    return max_val


def quantity(img):

    ret, img_bin = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY_INV)
    ocr.set_cand_alphabet("0123456789")
    res = ocr.ocr_for_single_line(img_bin)
    for i in range(res.count(" ")):
        res.remove(" ")
    resstr = ("".join(res))

    return resstr


def text(img, threshold):

    ret, img_bin = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY_INV)
    ocr.set_cand_alphabet(None)
    res = (ocr.ocr_for_single_line(img_bin))
    for i in range(res.count(" ")):
        res.remove(" ")
    resstr = ("".join(res))

    return resstr

    return res


def stage(img):

    ret, img_bin = cv2.threshold(img, 254, 255, cv2.THRESH_BINARY_INV)
    ocr.set_cand_alphabet("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-")
    res = (ocr.ocr_for_single_line(img_bin))
    for i in range(res.count(" ")):
        res.remove(" ")
    resstr = ("".join(res))

    return resstr
