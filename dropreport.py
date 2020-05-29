# -*- coding: utf-8 -*-

import json
import os
import sys
from time import sleep

import requests

from resolution import esc, hwnd

PenguinID = ""

while 1:
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
print("")
f = open("objective.json", encoding="utf-8")
objective = json.loads(f.read())
f.close()
for name, obj in objective["drops"].items():
    if obj != 0:
        name = f"【{name}】"
        space = 20 - len(name.encode('GBK')) + len(name)
        print(f"{name:<{space}s}{0:>3d}/{obj:>3d}{0:>13.2%}")
for i in range(40):
    print("-", end="")
print("")
print(f"已周回              {0:>3d}", end="")


def dropreport(report, count):

    global PenguinID
    index = report[0]
    data = report[1]

    def report_screen():
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
                droprate = quantity / count
                space = 20 - len(name.encode('GBK')) + len(name)
                if "·" in name:
                    space += 1
                print(
                    f"{name:<{space}s}{quantity:>3d}/{objective:>3d}{droprate:>13.2%}")

        for item in index.values():
            if item["quantity"] != 0 and item["objective"] == 0:
                name = "【" + item["name"] + "】"
                quantity = item["quantity"]
                droprate = quantity / count
                space = 20 - len(name.encode('GBK')) + len(name)
                if "·" in name:
                    space += 1
                print(f"{name:<{space}s}{quantity:>3d}{droprate:>17.2%}")
        for i in range(40):
            print("-", end="")
        print("")
        print(f"已周回              {count:>3d}", end="")

    url = "https://penguin-stats.io/PenguinStats/api/v2/report"
    cookie = {"userID": PenguinID}
    res = requests.post(url, cookies=cookie, json=data)
    status_code = res.status_code
    cookies = requests.utils.dict_from_cookiejar(res.cookies)
    if not os.path.exists("PenguinID.dat"):
        PenguinID = cookies["userID"]
        with open("PenguinID.dat", "w") as f:
            f.write(PenguinID)

    if status_code == 201:
        esc.press(hwnd)
        report_screen()
        sleep(1)
        print(f"         汇报成功")
        sleep(5)
        report_screen()
    else:
        esc.press(hwnd)
        report_screen()
        sleep(1)
        print(f"         汇报失败")
        sleep(5)
        report_screen()
