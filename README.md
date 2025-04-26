# OmoFun_Quiz

使用appium自动完成Lanerc(OmoFun)的入站问答

## Introduction

[OmoFun发布页](https://omoget.com/)

这是我随便写的一个项目,主要是想玩一玩appium,代码写的很烂

## Usage

1. 安装appium,配置好appium
2. 连接手机,开启adb调试,小米手机要同时打开`usb安装`和`usb调试(安全设置)`然后重启一下手机,可以先试试[appium inspector](https://github.com/appium/appium-inspector)能不能正常连接
3. 配置好python环境
4. 按需修改capabilities字典和appium_server_url,其中`deviceName`一定要改成你的手机名字,可以通过`adb devices`查看
5. 打开OmoFun,进入到入站问答界面(直接开始答题,屏幕上显示选项)
6. 运行main.py

## Env

- Appium-Python-Client (python package) [reference](https://appium.io/docs/zh/latest/quickstart/test-py/)
- appium (npm package) [reference](https://appium.io/docs/zh/latest/quickstart/install/)
- uiautomator2 (appium driver) [reference](https://appium.io/docs/zh/latest/quickstart/uiauto2-driver/)

## Files

- main.py: 主程序
- main.sqlite: 用于存储题目和答案的sqlite数据库
- old.sqlite: 用于存储题目和答案(旧版)的sqlite数据库
- README.md: 说明文档
- OmoFun.xlsx: OmoFun 题库 ,包含题目和答案,截止于2024/4/8,有一些题目还没有答案

## Screenshots

![开发者选项设置](/img/Screenshot_2024-04-09-08-59-09-932_com.android.se.jpg)
![OmoFun版本号](/img/Screenshot_2024-04-09-08-10-15-726_com.banshenghu.jpg)
![Lanerc](/img/Screenshot_2025-04-26-18-40-44-490_com.miui.secur.jpg)
