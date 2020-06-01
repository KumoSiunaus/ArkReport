#coding: utf-8

import json
import os
from time import sleep

import cv2
from win32 import win32api, win32gui

from dropcheck import *
from dropreport import dropreport
from preload import preload
from adapter import *

index, stage_code_to_id = preload(label)


def drop_check(img):
    stage_id = stage_code_to_id[find_stage(get_stage_image(img))]
    drop_type = get_drop_type(img)
    drop_image = get_drop_image(img, drop_type)
    drops = []
    with open("objective.json", encoding="utf-8") as f:
        objective = json.load(f)

    for type_ in drop_image:
        if drop_image[type_] == []:
            continue
        if type_ == "FURNITURE":
            drops.append({"dropType": type_, "itemId": "furni", "quantity": 1})
            continue

        for img_ in drop_image[type_]:
            item = ""
            similarity = 0
            location = []
            for item_ in index.values():
                if find_image(img_, item_["image"], loc=[]) > similarity:
                    similarity = find_image(img_, item_["image"], location)
                    item = item_["itemId"]

            if similarity > 0.5:
                drop_quantity = int(
                    find_quantity(get_quantity_image(img_, tuple(location))))
                index[item]["quantity"] += drop_quantity
                drops.append({
                    "dropType": type_,
                    "itemId": item,
                    "quantity": drop_quantity
                })

                if index[item]["objective"] > 0:
                    name = index[item]["name"]
                    objective["drops"][name] -= drop_quantity

    with open("objective.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(objective, ensure_ascii=False, indent=3))

    data = {
        "drops": drops,
        "stageId": stage_id,
        "server": label,
        "source": "ArkReport",
        "version": "v1.2.0"
    }

    report = (index, data)
    return report


if __name__ == "__main__":

    print()

    count = 0

    while True:

        img = get_image()

        while not find_text(img[end.top:end.bottom, end.left:end.right],
                            254) == "行动结束":
            img = get_image()
            sleep(1)

        sleep(3)
        device.swipe((simulator_win.width - 10, baseline_h.top),
                     (simulator_win.width - 6 * drop.width, baseline_h.top))
        img = get_image()
        report = drop_check(img)
        count += 1
        dropreport(report, count)
        sleep(5)
        print(f"\r已周回              {count:>3d}                 ")
        sleep(60)
