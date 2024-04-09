# OmoFun_Quiz
使用appium自动完成OmoFun的入站问答

## Introduction

这是我随便写的一个项目,主要是想玩一玩appium,代码写的很烂

## Usage

1. 安装appium,配置好appium
2. 连接手机,开启adb调试,小米手机要同时打开`usb安装`和`usb调试(安全设置)`然后重启一下手机,可以先试试[appium inspector](https://github.com/appium/appium-inspector)能不能正常连接
3. 配置好python环境
4. 按需修改capabilities字典和appium_server_url,其中`deviceName`一定要改成你的手机名字,可以通过`adb devices`查看
5. 打开OmoFun,进入到入站问答界面(直接开始答题,屏幕上显示选项)
6. 运行main.py

## Note

脚本写的不太完善,答满42道题会进入无限循环,手动停止脚本提交答案即可

## Files

- main.py: 主程序
- main.sqlite: 用于存储题目和答案的sqlite数据库
- README.md: 说明文档
- OmoFun.xlsx: 题库,包含题目和答案,有一些题目还没有答案


## Screenshots
![开发者选项设置](/img/Screenshot_2024-04-09-08-59-09-932_com.android.se.jpg)
![OmoFun版本号](/img/Screenshot_2024-04-09-08-10-15-726_com.banshenghu.jpg)
