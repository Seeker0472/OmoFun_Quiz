# import appium
from time import sleep
import re

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

import sqlite3

capabilities = dict(
    platformName='Android',
    automationName='UiAutomator2',
    deviceName='38fe22a5',
    appPackage='com.banshenghuo.mobile.ofdm',
    appActivity='com.banshenghuo.mobile.ofdm.MainActivity',
    platformVersion="14",
    noReset=True
)
appium_server_url = 'http://localhost:4723'

driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
#
# el2 = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="入站问答")
# el2.click()
# sleep(2)
# el3 = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="开始答题")
# el3.click()
chinese_pattern = re.compile(r'[A-Z]\..*')  # 匹配中文字符的正则表达式范围

conn = sqlite3.connect('main.sqlite')


def main():
    i = 0
    while True:
        # 检查是不是所有题目都有答案
        i += 1
        if i > 300 and check_db():
            return 0
        else:
            i = 0
        already_known = False
        cursor = conn.cursor()
        # 判断是否是ScrollView
        class_view = driver.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().className("
                                                                                 "\"android.view.View\")")
        class_scroll = driver.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().className("
                                                                                   "\"android.widget.ScrollView\")")
        # print(len(class_view))
        prev_cnt = class_view[len(class_view) - 3].tag_name
        # print(class_view[len(class_view) - 3].tag_name)
        parent_view = None
        if len(class_scroll) == 0:
            parent_view = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR,
                                              value="new UiSelector().className(\"android.view.View\").instance(7)")
        else:
            parent_view = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().className("
                                                                                     "\"android.widget.ScrollView\")")

        # 在父元素内部，查找所有的android.view.View子元素
        options = parent_view.find_elements(by=AppiumBy.CLASS_NAME, value="android.view.View")

        i = 0
        Title_index = -1
        ans = [-1, -1]
        # 遍历这些子元素,找到题目和选项的位置
        for i in range(len(options)):
            # 获取每个选项的content-desc属性值
            content_desc = options[i].get_attribute("contentDescription")
            # print(content_desc)
            if content_desc.find('￼\n￼\n') != -1:
                Title_index = i
                continue
            if bool(chinese_pattern.match(content_desc)):
                if ans[0] == -1:
                    ans[0] = i
                    ans[1] = i
                else:
                    ans[1] = i

        num = cursor.execute("select id from Texts where text=(?)",
                             (options[Title_index].get_attribute("contentDescription"),)).fetchall()
        if len(num) == 0:
            cursor.execute("insert into Texts (text) values (?)",
                           (options[Title_index].get_attribute("contentDescription"),))
            conn.commit()
            num = cursor.execute("select id from Texts where text=?",
                                 (options[Title_index].get_attribute("contentDescription"),)).fetchall()[0]
        else:
            num = num[0]
        db_ans = cursor.execute("select id,content,ok from Answers where text_id=(?)", (num[0],)).fetchall()

        items_to_test = None

        # 如果答案未找到
        if len(db_ans) == 0:
            for i in range(ans[0], ans[1] + 1):
                cursor.execute("insert into Answers (text_id,content,ok) values (?,?,?)",
                               (num[0], options[i].get_attribute("contentDescription"), 0))
            conn.commit()
            db_ans = cursor.execute("select id,content,ok from Answers where text_id=(?)", (num[0],)).fetchall()
            items_to_test = ans[0]
        else:
            # 找到未答的选项
            for i in range(len(db_ans)):
                # if db_ans[i][2] == 2:
                #     # 乱答
                #     print("乱答")
                #     already_known = True
                #     items_to_test = 0
                #     break
                if db_ans[i][2] == 0 or db_ans[i][2] == 2:
                    items_to_test = i
                    break

        offset = -1
        for i in range(ans[0], ans[1] + 1):
            # print(options[i].get_attribute("contentDescription"))
            if options[i].get_attribute("contentDescription") == db_ans[items_to_test][1]:
                offset = i
                break

        options[offset].click()
        sleep(0.3)
        view_after = driver.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().className("
                                                                                 "\"android.view.View\")")
        if not already_known:
            if prev_cnt == view_after[len(view_after) - 3].tag_name:
                print("答错了!")
                cursor.execute("update Answers set ok=1 where id=?", (db_ans[items_to_test][0],))
            else:
                print("答对了!")
                cursor.execute("update Answers set ok=2 where id=?", (db_ans[items_to_test][0],))

        conn.commit()


def check_db():
    unknown = 0
    cursor = conn.cursor()
    all_id = cursor.execute("select id from Texts").fetchall()
    for i in all_id:
        all_ans = cursor.execute("select ok from Answers where text_id=?", (i[0],)).fetchall()
        if 2 not in [x[0] for x in all_ans]:
            unknown += 1
    print("未知:"+str(unknown))
    if unknown == 0:
        return True
    else:
        return False
    # pass


def GO():
    try:
        main()
    except Exception as e:
        GO()


if __name__ == '__main__':
    GO()
    # check_db()
    driver.quit()
