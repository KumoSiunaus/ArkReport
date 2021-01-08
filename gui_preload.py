import os
import json
import cv2
import requests


def get_stageindex():
    url = "https://penguin-stats.io/PenguinStats/api/v2/stages"
    with requests.get(url) as f:
        stage_table = json.loads(f.content.decode())

    stage_index = {}
    for stage in stage_table:
        code = stage["code"]
        stageId = stage["stageId"]
        drops = []
        if "dropInfos" in stage:
            for item in stage["dropInfos"]:
                if "itemId" in item:
                    if not item["itemId"] == "furni":
                        drops.append(item["itemId"])
        stage_index[code] = {"stageId": stageId, "drops": drops}

    return stage_index


def get_itemindex():
    url = "https://penguin-stats.io/PenguinStats/api/v2/items"
    with requests.get(url) as f:
        item_table = json.loads(f.content.decode())

    item_index = {}
    for item in item_table:
        itemId = item["itemId"]
        name_i18n = item["name_i18n"]
        img = cv2.imread(f"resource\\items2\\{itemId}.png")
        if not img is None:
            item_index[itemId] = {"name_i18n": name_i18n, "img": img}

    return item_index


stage_index = get_stageindex()
item_index = get_itemindex()
droptype_index = {
    "常规掉落": "NORMAL_DROP",
    "特殊掉落": "SPECIAL_DROP",
    "额外物资": "EXTRA_DROP",
    "幸运掉落": "FURNITURE"
}

if __name__ == "__main__":

    item_index = get_itemindex()
    cv2.imshow("", item_index["2003"]["img"])
    cv2.waitKey(0)