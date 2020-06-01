# ArkReport
明日方舟掉落检测 数据提供至企鹅物流 | Drop Check of Arknights, data to Penguin Statistics
## 0x00 Introduction
本项目是基于OCR与Template Matching的明日方舟掉落识别工具。所收集的掉落数据通过API全部提交至企鹅物流数据统计( https://penguin-stats.io )， 旨在通过自动提交掉落报告，提供更多掉落样本，为广大博士提供更精确的掉落率数据。

## 0x01 Installation
安装依赖
$ pip install -r requirements.txt

## 0x02 Usage
**注意：请务必将模拟器调整为2：1之分辨率，推荐2160\*1080**
**本项目基于MuMu模拟器编写，因此优先推荐使用MuMu模拟器。已做屏幕多分辨率适配及多模拟器适配，可移动窗口或缩放窗口（由于会影响ocr识别，因此不建议进行过度缩小，推荐窗口最大化），遮挡也不会对检测产生影响。**

可在objective.json文件内加入希望刷的材料及数量，程序会提供计数，若有目标掉落本地文件也会更改，因此在下次运行时您无需再次设置。

程序入口为【dropcheck.py】，首次运行会要求您输入PenguinID，如果您没有，请直接按回车进入程序，在第一次数据汇报成功后您将会获得PenguinID并记录储存，已记录的ID在下次无需再次登录。如果您希望更改PenguinID，请删除PenguinID.dat文件

登入后正常刷图即可，程序提供了 掉落名称/掉落数量（目标数量）/掉落率/刷图次数 等数据。在结束战斗后的掉落界面不要手动退出，直到程序显示“汇报成功”（部分模拟器可自动退出）。
