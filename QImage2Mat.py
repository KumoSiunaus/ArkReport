# -*- coding: utf-8 -*-

import numpy


def QImage2Mat(img):
    ptr = img.constBits()
    ptr.setsize(img.byteCount())

    mat = numpy.array(ptr).reshape(
        img.height(), img.width(), 4)  # 注意这地方通道数一定要填4，否则出错
    return mat
