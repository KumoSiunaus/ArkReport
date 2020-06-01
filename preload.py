#coding: utf-8

import json
import os

import cv2


def preload(label):

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    index = {}  # item dict

    os.chdir("resource")
    with open("item_table.json", encoding="utf-8") as f:
        item_table = json.loads(f.read())
    with open("stage_table.json", encoding="utf-8") as f:
        stage_table = json.loads(f.read())

    stage_code_to_id = {}
    for stage_ in stage_table["stages"]:

        code = stage_table["stages"][stage_]["code"]
        stage_id = stage_table["stages"][stage_]["stageId"]
        difficulty = stage_table["stages"][stage_]["difficulty"]

        if difficulty == "NORMAL":
            stage_code_to_id[code] = stage_id

    os.chdir("items")
    index = {}
    item_name_to_id = {}
    for png in os.listdir():
        item_id = os.path.splitext(png)[0]
        name = item_table["items"][item_id]["name"]
        item = item_id
        index[item] = {}
        index[item]["name"] = name
        index[item]["itemId"] = item_id
        index[item]["image"] = cv2.imread(png, cv2.IMREAD_COLOR)[41:141,
                                                                 41:141]
        index[item]["quantity"] = 0
        index[item]["objective"] = 0
        item_name_to_id[name] = item_id

    os.chdir("../../")

    with open("objective.json", encoding="utf-8") as f:
        objective = json.loads(f.read())
    for stage_ in objective["drops"]:
        item = item_name_to_id[stage_]
        quantity = objective["drops"][stage_]
        index[item]["objective"] = quantity

    return index, stage_code_to_id
