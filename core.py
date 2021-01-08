# coding: utf-8
import asyncio
import os
import threading
import time
from typing import Any, Callable

import cv2
import numpy as np
from cnocr import CnOcr

from gui_preload import item_index, stage_index, droptype_index
from gui_simulator import simulator

TOP = 0
BOTTOM = 1
LEFT = 2
RIGHT = 3
BEGIN = 0
END = 1

HASH_RESULT = np.array([[241, 15, 78, 228, 15, 131, 58, 184]], dtype=np.uint8)
HASH_NORMAL = np.array([[157, 255, 38, 100, 176, 236, 150, 154]],
                       dtype=np.uint8)
HASH_SPECIAL = np.array([[89, 255, 36, 85, 134, 232, 222, 187]],
                        dtype=np.uint8)
HASH_EXTRA = np.array([[223, 251, 196, 150, 38, 162, 24, 201]], dtype=np.uint8)
HASH_FURNITURE = np.array([[29, 140, 48, 94, 240, 239, 48, 158]],
                          dtype=np.uint8)

loop = asyncio.new_event_loop()
ocr = CnOcr()


def show_img(img):
    cv2.imshow("", img)
    cv2.waitKey(0)


def set_threading(loop: asyncio.AbstractEventLoop = loop):
    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    threading.Thread(target=run_loop, daemon=True).start()


class Img(np.ndarray):
    def __new__(cls, img: np.ndarray):
        instance = img.view(cls)
        instance.height = img.shape[0]
        instance.width = img.shape[1]
        if img.ndim == 2:
            instance.channel = 1
        elif img.ndim == 3:
            instance.channel = img.shape[2]
        return instance

    def __array_finalize__(self, instance):
        if instance is None:
            return
        if self.ndim >= 2:
            if self.ndim == instance.ndim:
                self.height = self.shape[0]
                self.width = self.shape[1]
            self.channel = getattr(instance, "channel", None)

    @classmethod
    def read(cls, filename, flag=1):
        img: np.ndarray = cv2.imread(filename, flag)
        if flag == 0:
            instance: Img = img.view(cls)
            instance.height = instance.shape[0]
            instance.width = instance.shape[1]
            instance.channel = 1
            return instance
        elif (flag == -1) or (flag == 1):
            instance: Img = img.view(cls)
            instance.height = instance.shape[0]
            instance.width = instance.shape[1]
            instance.channel = instance.shape[2]
            return instance

    def bgr(self):  # GRAY -> BGR
        return Img(cv2.cvtColor(self, cv2.COLOR_GRAY2BGR))

    def gray(self):  # BGR -> GRAY
        return Img(cv2.cvtColor(self, cv2.COLOR_BGR2GRAY))

    def bin(self, threshold):  # GRAY -> BINARY
        return Img(cv2.threshold(self, threshold, 255, cv2.THRESH_BINARY)[1])

    def blur(self):  # BGR -> GRAY
        return Img(cv2.medianBlur(self, 11))

    def mask(self):  # BGR(GRAY) -> BGR(GRAY)
        if self.channel == 1:
            return self.bin(0)
        elif self.channel == 3:
            return self.gray().bin(0).bgr()

    def resize(self, fx):
        if self.channel == 1:
            return Img(cv2.resize(self, None, fx=fx, fy=fx))
        if self.channel == 3:
            return Img(cv2.resize(self, None, fx=fx, fy=fx))

    def min_rect(self):  # BIN -> BIN
        top = 0
        bottom = 0
        left = 0
        right = 0
        for i in range(self.height):
            if self[i, :].any():
                top = i
                break
        for i in range(self.height - 1, -1, -1):
            if self[i, :].any():
                bottom = i + 1
                break
        for i in range(self.width):
            if self[:, i].any():
                left = i
                break
        for i in range(self.width - 1, -1, -1):
            if self[:, i].any():
                right = i + 1
                break
        res: Img = self[top:bottom, left:right]
        return res

    def phash(self):
        return cv2.img_hash.PHash_create().compute(self)


class Result:

    hash_dict = {
        "常规掉落": HASH_NORMAL,
        "特殊掉落": HASH_SPECIAL,
        "额外物资": HASH_EXTRA,
        "幸运掉落": HASH_FURNITURE,
    }

    def __init__(self, img: Img, baseline_v) -> None:
        self.img = img
        self.baseline_v = baseline_v
        self.baseline_h = self.get_baseline_h(img, baseline_v)
        self.item_diameter = round(
            (baseline_v[BOTTOM] - baseline_v[TOP]) * 0.52)

        self.drops = []
        self.drops_display = {}
        self.stage_code = ""
        self.droptype = {}

    @staticmethod
    def get_baseline_v(img: Img):
        img_bin127 = img.gray().bin(127)
        column = 0
        top = 0
        bottom = 0
        for i in range(img.width // 4, img.width // 2):
            col = img_bin127[:, i]
            begin = 0
            end = 0
            iand = False
            ior = False
            for j in range(len(col) - 1, -1, -1):
                iand = iand and bool(col[j])
                ior = ior or bool(col[j])
                if iand ^ ior:
                    iand = True
                    ior = True
                    if not (begin ^ end):
                        end = j + 1
                    else:
                        begin = j + 1
                if begin and end:
                    break
            if end - begin > bottom - top:
                column = i
                top = begin
                bottom = end
        return (top, bottom, column, column)

    @staticmethod
    def get_baseline_h(img: Img, baseline_v):
        img_bin127 = img.gray().bin(127)
        min_r = (baseline_v[BOTTOM] - baseline_v[TOP]) // 4
        row = 0
        left = 0
        right = 0
        for i in range(baseline_v[BOTTOM], baseline_v[TOP], -1):
            r = img_bin127[i, :]
            begin = 0
            end = 0
            iand = False
            ior = False
            for j in range(baseline_v[RIGHT] + 10, img.width):
                iand = iand and bool(r[j])
                ior = ior or bool(r[j])
                if iand ^ ior:
                    iand = True
                    ior = True
                    if not (begin ^ end):
                        begin = j
                    else:
                        end = j
                if begin and end:
                    break
            if end - begin > right - left:
                row = i
                left = begin
                right = end
            if (not iand) and (not ior) and (right - left > min_r):
                break
        return (row, row, left, right)

    @classmethod
    async def preanalyse(cls, img: Img):
        baseline_v = Result.get_baseline_v(img)
        valid = await asyncio.gather(Result.is_end(img, baseline_v),
                                     Result.is_3stars(img, baseline_v))
        if all(valid): return cls(img, baseline_v)
        else: return False

    @staticmethod
    async def analyse(img: Img = None, result=None):
        if (img is None) and (result is None):
            raise ValueError("Nothing to analyse")
        if img is None:
            img = result.img
        elif result is None:
            result = await Result.preanalyse(img)

        if result is False:
            return None
        await asyncio.gather(result.get_stage(), result.get_droptype())
        await result.get_drops()
        data = {
            "drops": result.drops,
            "stageId": stage_index[result.stage_code]["stageId"]
        }
        display = f"{result.stage_code}{result.drops_display}"
        return data, display

    @staticmethod
    async def is_end(img, baseline_v=None):
        if baseline_v is None:
            baseline_v = Result.get_baseline_v(img)
        img_bin127: Img = img.gray().bin(
            127)[(baseline_v[TOP] + baseline_v[BOTTOM]) //
                 2:baseline_v[BOTTOM], :baseline_v[LEFT] - 5, ]

        img_min_rect = img_bin127.min_rect()
        if not img_min_rect.size > 0: return False
        diff = int(cv2.img_hash.PHash_create().compare(
            img_bin127.min_rect().phash(), HASH_RESULT))
        if diff <= 12: return True
        else: return False

    @staticmethod
    async def is_3stars(img, baseline_v=None):
        if baseline_v is None:
            baseline_v = Result.get_baseline_v(img)
        img_bin127 = img.gray().bin(127)[
            baseline_v[TOP]:baseline_v[BOTTOM], :baseline_v[LEFT]]
        begin = 0
        end = 0
        iand = False
        ior = False
        for i in range(img_bin127.width - 1, -1, -1):
            iand = iand and any(img_bin127[:, i])
            ior = ior or any(img_bin127[:, i])
            if iand ^ ior:
                iand = True
                ior = True
                if not (begin ^ end):
                    end = i + 1
                else:
                    begin = i + 1
            if begin and end:
                break
        img_bin127 = img_bin127[:img_bin127.height // 2, begin:end]
        if any([any(r) for r in img_bin127]):
            return True
        else:
            return False

    async def get_stage(self) -> str:
        img_bin215 = self.img.gray().bin(215)[self.baseline_v[TOP]:(
            3 * self.baseline_v[TOP] + self.baseline_v[BOTTOM]) //
                                              4, :self.baseline_v[LEFT], ]
        ocr.set_cand_alphabet("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-")
        stage_code = "".join(ocr.ocr_for_single_line(img_bin215))
        self.stage_code = stage_code

    async def get_droptype(self):

        img_bin127 = self.img.gray().bin(127)
        droptype = {}
        row = img_bin127[self.baseline_h[TOP]]
        begin = 0
        end = 0
        iand = False
        ior = False
        for i in range(self.baseline_h[RIGHT], self.img.width):
            if begin and end:  # line of droptype detected
                img_droptype: Img = self.img[self.baseline_h[TOP] +
                                             1:self.baseline_v[BOTTOM],
                                             begin:end]
                threshold = int(img_droptype.gray().max() // 2)
                img_droptype = img_droptype.gray().bin(threshold).min_rect()
                # compare hash
                diff = 64
                dtype = ""
                for type_, hash_ in Result.hash_dict.items():
                    d = cv2.img_hash.PHash_create().compare(
                        img_droptype.phash(), hash_)
                    if d < diff:
                        diff = d
                        dtype = type_
                droptype[dtype] = (begin, end)

                begin = 0
                end = 0
                iand = False
                ior = False
            iand = iand and bool(row[i])
            ior = ior or bool(row[i])
            if iand ^ ior:
                iand = True
                ior = True
                if not (begin or end):
                    begin = i
                else:
                    end = i
        self.droptype = droptype

    async def detect_item(self, dropimg: Img):
        itemId = ""
        item_name = ""
        similarity = 0
        location = (0, 0)
        for itemId_ in stage_index[self.stage_code]["drops"]:
            item_ = item_index[itemId_]
            itemimg = Img(item_["img"])
            templ = itemimg.resize(self.item_diameter / 163)
            mask = templ.mask()
            res = cv2.minMaxLoc(
                cv2.matchTemplate(dropimg,
                                  templ,
                                  cv2.TM_CCORR_NORMED,
                                  mask=mask))
            if res[1] > similarity:
                itemId = itemId_
                similarity = res[1]
                location = res[3]
        width = round(183 * (self.item_diameter / 163))
        dropimg = dropimg[location[0]:location[0] + width,
                          location[1]:location[1] + width]
        quantity = await self.detect_quantity(dropimg)
        return (itemId, quantity, similarity)

    async def detect_quantity(self, dropimg: Img):
        qimg: Img = dropimg[round(dropimg.height *
                                  0.7):round(dropimg.height *
                                             0.85), :round(dropimg.width *
                                                           0.82), ]
        qimg_bin127 = qimg.gray().bin(127)
        begin = 0
        edge_width = 0
        count = 0
        for col in range(qimg.width - 1, -1, -1):
            ior = False
            for pix in qimg_bin127[:, col]:
                ior = ior or bool(pix)
            if not ior:
                count = count + 1
            else:
                if not edge_width:
                    edge_width = count
                count = 0
            if edge_width and count >= edge_width:
                begin = col
                break
        qimg = qimg_bin127[:, begin:]
        ocr.set_cand_alphabet("1234567890万")
        quantity = "".join(ocr.ocr_for_single_line(qimg))
        return quantity

    async def get_drops(self):
        drops = []
        if self.droptype:
            for type_, range_ in self.droptype.items():
                if type_ == "幸运掉落":
                    drops.append({
                        "dropType": droptype_index[type_],
                        "itemId": "furni",
                        "quantity": 1
                    })
                    self.drops_display["家具"] = True
                    continue
                range_length = range_[END] - range_[BEGIN]
                count = range_length // self.item_diameter
                for i in range(count):
                    item_range = (
                        range_[BEGIN] + i * range_length // count,
                        range_[BEGIN] + (i + 1) * range_length // count,
                    )
                    dropimg = self.img[(3 * self.baseline_v[TOP] +
                                        self.baseline_v[BOTTOM]) //
                                       4:self.baseline_h[TOP],
                                       item_range[BEGIN]:item_range[END], ]
                    itemId, quantity, similarity = await self.detect_item(
                        dropimg)
                    if similarity > 0.9:
                        drops.append({
                            "dropType": droptype_index[type_],
                            "itemId": itemId,
                            "quantity": quantity
                        })
                        name = item_index[itemId]["name_i18n"]["zh"]
                        if name in self.drops_display:
                            self.drops_display[name] += quantity
                        else:
                            self.drops_display[name] = quantity
        self.drops = drops


async def img_analyse(signal):
    while True:
        img = Img(await simulator.screenshot())
        if img is None: continue
        if result := await Result.preanalyse(img):
            await asyncio.sleep(5)
            simulator.swipe((result.img.width - 10, result.baseline_h[TOP]),
                            (result.baseline_h[LEFT], result.baseline_h[TOP]))
            img = Img(await simulator.screenshot())
            if res := await Result.analyse(img):
                data, display = res
                signal.emit(display)
                simulator.click(
                    (result.img.width // 2, result.img.height // 2))


if __name__ == "__main__":

    async def test():
        # for png in os.listdir("adb\\test"):
        #     img = Img(cv2.imread("adb\\test\\" + png))
        img = Img.read("adb\\c.png")
        if result := await Result.analyse(img):
            data, display = result
            print(data, display)

    asyncio.run(test())

    # import cProfile
    # cProfile.run("asyncio.run(test())")
