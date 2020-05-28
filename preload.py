# -*- coding: utf-8 -*-

import os
import json
import cv2


def preload(label):

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    index = {}  # item管理字典

    os.chdir("resource")
    f = open("item_table.json", encoding="utf-8")
    item_table = json.loads(f.read())
    f.close()

    f = open("stage_table.json", encoding="utf-8")
    stage_table = json.loads(f.read())
    f.close()
    stageCode2Id = {}
    for key in stage_table["stages"]:

        code = stage_table["stages"][key]["code"]
        stageId = stage_table["stages"][key]["stageId"]
        difficulty = stage_table["stages"][key]["difficulty"]

        if difficulty == "NORMAL":
            stageCode2Id[code] = stageId

    os.chdir("items")
    index = {}
    itemName2Id = {}
    for png in os.listdir():
        itemId = os.path.splitext(png)[0]
        name = item_table["items"][itemId]["name"]
        item = itemId
        index[item] = {}
        index[item]["name"] = name
        index[item]["itemId"] = itemId
        index[item]["image"] = cv2.imread(
            png, cv2.IMREAD_COLOR)[41:141, 41:141]
        index[item]["quantity"] = 0
        index[item]["objective"] = 0
        itemName2Id[name] = itemId

    os.chdir("../../")

    f = open("objective.json", encoding="utf-8")
    objective = json.loads(f.read())
    f.close()
    for key in objective["drops"]:
        item = itemName2Id[key]
        quantity = objective["drops"][key]
        index[item]["objective"] = quantity

    return index, stageCode2Id
