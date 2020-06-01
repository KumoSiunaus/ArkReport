#coding: utf-8

import json
import os
import sys
from time import sleep

import requests
from win32 import win32api

from adapter import esc, focus, hwnd

PenguinID = ""

while True:

    os.system("cls")

    if os.path.exists("PenguinID.dat"):
        with open("PenguinID.dat") as f:
            PenguinID = f.read()
    else:
        PenguinID = input("请输入PenguinID：")
    respond = requests.post(
        "https://penguin-stats.io/PenguinStats/api/v2/users", data=PenguinID)

    if respond.status_code == 200:
        os.system("cls")
        print(f"已登录为：PenguinID# {PenguinID}")
        with open("PenguinID.dat", "w") as f:
            f.write(PenguinID)
        break
    elif respond.status_code == 400:
        os.system("cls")
        print("未登录 PenguinID#")
        break
    elif respond.status_code == 404:
        os.system("cls")
        print("登录失败：未找到此用户ID。请注意这不是游戏内的ID。在本站汇报一次掉落数据即可自动获得。")
        sleep(3)

for i in range(40):
    print("-", end="")
print()

with open("objective.json", encoding="utf-8") as f:
    objective = json.loads(f.read())

for item_, quantity_ in objective["drops"].items():
    if quantity_ != 0:
        item_ = f"【{item_}】"
        space = 20 - len(item_.encode('GBK')) + len(item_)
        print(f"{item_:<{space}s}{0:>3d}/{quantity_:>3d}{0:>13.2%}")

for i in range(40):
    print("-", end="")
print()

print(f"已周回              {0:>3d}", end="", flush=True)


def dropreport(report, count):

    global PenguinID
    index = report[0]
    data = report[1]

    def report_to_screen():

        os.system("cls")

        if PenguinID == "":
            print("未登录 PenguinID#")
        else:
            print(f"已登录为：PenguinID# {PenguinID}")
        for i in range(40):
            print("-", end="")
        print("")

        for item in index.values():
            if item["objective"] != 0:
                name = "【" + item["name"] + "】"
                quantity = item["quantity"]
                objective = item["objective"]
                drop_rate = quantity / count
                space = 20 - len(name.encode('GBK')) + len(name)
                if "·" in name:
                    space += 1
                print(
                    f"{name:<{space}s}{quantity:>3d}/{objective:>3d}{drop_rate:>13.2%}"
                )

        for item in index.values():
            if item["quantity"] != 0 and item["objective"] == 0:
                name = "【" + item["name"] + "】"
                quantity = item["quantity"]
                drop_rate = quantity / count
                space = 20 - len(name.encode('GBK')) + len(name)
                if "·" in name:
                    space += 1
                print(f"{name:<{space}s}{quantity:>3d}{drop_rate:>17.2%}")
        for i in range(40):
            print("-", end="")
        print()

        print(f"已周回              {count:>3d}", end="", flush=True)

    url = "https://penguin-stats.io/PenguinStats/api/v2/report"
    cookie = {"userID": PenguinID}
    res = requests.post(url, cookies=cookie, json=data)
    status_code = res.status_code
    cookies = requests.utils.dict_from_cookiejar(res.cookies)
    if not os.path.exists("PenguinID.dat"):
        PenguinID = cookies["userID"]
        with open("PenguinID.dat", "w") as f:
            f.write(PenguinID)

    report_to_screen()
    if status_code == 201:
        print(f"         汇报成功", end="", flush=True)
    else:
        print(f"         汇报失败", end="", fulsh=True)
    focus(hwnd)
    esc.press(hwnd)
