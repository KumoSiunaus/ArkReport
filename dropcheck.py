# -*- coding: utf-8 -*-

import get
import find
import cv2
import os
import json
from pyautogui import sleep
from preload import preload
from resolution import *
from dropreport import dropreport


index, stageCode2Id = preload(label)


def dropcheck(img):
    stageId = stageCode2Id[find.stage(get.stageimg(img))]
    droptype = get.droptype(img)
    dropimg = get.dropimg(img, droptype)
    drops = []
    with open("objective.json", encoding="utf-8") as f:
        objective = json.load(f)

    for Type in dropimg:
        if dropimg[Type] == []:
            continue
        if Type == "FURNITURE":
            drops.append({"dropType": Type, "itemId": "furni", "quantity": 1})
            continue

        for img_sp in dropimg[Type]:
            Item = ""
            similarity = 0
            loc = []
            for item in index.values():
                if find.image(img_sp, item["image"], loc=[]) > similarity:
                    similarity = find.image(img_sp, item["image"], loc)
                    Item = item["itemId"]

            if similarity > 0.5:
                quantity = int(find.quantity(
                    get.quantityimg(img_sp, tuple(loc))))
                index[Item]["quantity"] += quantity
                drops.append(
                    {"dropType": Type, "itemId": Item, "quantity": quantity})

                if index[Item]["objective"] != 0:
                    name = index[Item]["name"]
                    objective["drops"][name] -= quantity

    with open("objective.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(objective, ensure_ascii=False, indent=3))

    data = {"drops": drops, "stageId": stageId, "server": label,
            "source": "ArkReport", "version": "v1.0.0"}

    report = (index, data)
    return report


if __name__ == "__main__":

    print()

    count = 0

    while 1:
        img = get.image(hwnd)
        while not find.text(img[end.top:end.bottom, end.left:end.right], 254) == "行动结束":
            img = get.image(hwnd)
            sleep(2)
        sleep(5)
        img = get.image(hwnd)
        report = dropcheck(img)
        count += 1
        dropreport(report, count)
        print()
        esc.press(hwnd)
        sleep(60)
