import requests

url = "https://penguin-stats.io/PenguinStats/api/v2/users"


def login(PenguinID=input) -> str:

    if type(PenguinID) is type(input):
        PenguinID = PenguinID("请输入PenguinID：")

    with requests.post(url, PenguinID) as res:
        if res.status_code == 200:
            with open("PenguinID.dat", "w", encoding="utf-8") as f:
                f.write(PenguinID)
            return "accepted"
        elif res.status_code == 400:
            return "blank"
        elif res.status_code == 404:
            return "rejected"