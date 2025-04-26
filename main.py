from time import sleep
import logging
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import sqlite3

##################################
# Configs
##################################

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
random_answer = False
capabilities = dict(
    platformName='Android',
    automationName='UiAutomator2',
    deviceName='bd5e4c5a',
    appPackage='com.xuzly.hy.lanerc.app',
    appActivity='com.xuzly.hy.lanerc.app.MainActivity',
    platformVersion="15",
    noReset=True
)
appium_server_url = 'http://localhost:4723'


logging.getLogger("appium").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

driver = None
conn = None


def main():
    i = 0
    while True:
        # 检查是不是所有题目都有答案
        i += 1
        if i > 300 and check_db():
            return 0
        else:
            i = 0
        cursor = conn.cursor()

        appium_question, appium_options = find_question_ans()
        prev_cnt = get_cnt()

        question_id = get_or_store_question(appium_question, cursor)
        offset, already_known, items_to_test, db_ans = get_or_store_answer(
            question_id, appium_options, cursor)

        appium_options[offset].click()
        sleep(0.3)
        if not already_known:
            now_cnt = get_cnt()
            if prev_cnt == now_cnt:
                logging.info("答错了!")
                update_answer(cursor, db_ans[items_to_test][0], 1)
                # cursor.execute("update Answers set ok=1 where id=?", (db_ans[items_to_test][0],))
            else:
                logging.info("答对了!")
                update_answer(cursor, db_ans[items_to_test][0], 2)
                # cursor.execute("update Answers set ok=2 where id=?", (db_ans[items_to_test][0],))

        conn.commit()


def update_answer(cursor, answer_id, okey):
    """
    更新答案的正确性
    :param cursor: 数据库游标
    :param answer_id: 答案的id
    :param okey: 答案的正确性
    """
    cursor.execute("update Answers set ok=? where id=?", (okey, answer_id))
    conn.commit()
    logging.info("DB:更新答案成功")


def get_or_store_answer(question_id, options, cursor):
    """
    获取题目的答案,如果没有就插入
    :param question_id: 题目的id
    :param options: 答案
    :param cursor: 数据库游标
    :return offset: 答案的偏移量
    :return already_known: 是否已经知道答案
    :return items_to_test: 选择的答案
    :return db_ans: 数据库查询记录
    """
    db_ans = cursor.execute(
        "select id,content,ok from Answers where text_id=(?)", (question_id[0],)).fetchall()

    items_to_test = None
    already_known = False

    # 如果答案未找到
    if len(db_ans) == 0:
        for i in range(0, len(options)):
            cursor.execute("insert into Answers (text_id,content,ok) values (?,?,?)",
                           (question_id[0], options[i].get_attribute("contentDescription"), 0))
        conn.commit()
        db_ans = cursor.execute(
            "select id,content,ok from Answers where text_id=(?)", (question_id[0],)).fetchall()
        items_to_test = 0
    else:
        # 找到未答的选项
        for i in range(len(db_ans)):
            if db_ans[i][2] == 2 and random_answer:
                # 选择第一个,为了爬题库
                logging.info("答案已知,选择第一个")
                already_known = True
                items_to_test = 0
                break
            if db_ans[i][2] == 0 or db_ans[i][2] == 2:
                items_to_test = i
                break

    offset = -1
    for i in range(len(options)):
        logging.info(
            f"比较选项---{options[i].get_attribute("contentDescription")}")
        if str(options[i].get_attribute("contentDescription")) == db_ans[items_to_test][1]:
            offset = i
            break
    return offset, already_known, items_to_test, db_ans


def get_or_store_question(question, cursor):
    """
    获取题目的id,如果没有就插入
    :param question: 题目
    :param cursor: 数据库游标
    :return: 题目的id
    """
    question_id = cursor.execute("select id from Texts where text=(?)",
                                 (question.get_attribute("content-desc"),)).fetchall()
    if len(question_id) == 0:
        cursor.execute("insert into Texts (text) values (?)",
                       (question.get_attribute("contentDescription"),))
        conn.commit()
        question_id = cursor.execute("select id from Texts where text=?",
                                     (question.get_attribute("contentDescription"),)).fetchall()[0]
    else:
        question_id = question_id[0]
    logging.debug(f"DB:题目ID: {question_id[0]}")
    return question_id


def check_db():
    unknown = 0
    cursor = conn.cursor()
    all_id = cursor.execute("select id from Texts").fetchall()
    for i in all_id:
        all_ans = cursor.execute(
            "select ok from Answers where text_id=?", (i[0],)).fetchall()
        if 2 not in [x[0] for x in all_ans]:
            unknown += 1
    logging.warning(">>>-----<<<程序开始>>>-----<<<")
    logging.warning(">>>---当前数据库答案未知题目:"+str(unknown)+"---<<<")
    if unknown == 0:
        return True
    else:
        return False


def init():
    global driver, conn
    driver = webdriver.Remote(
        appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
    conn = sqlite3.connect('main.sqlite')


def quit():
    global driver
    driver.quit()
    conn.close()


########################
# 屏幕上抓取内容的函数
########################

def find_question_ans():
    """
    从屏幕上抓取当前的题目和答案,可能需要适配
    return: question:题目,appium_options:答案
    """
    # 查找所有 class name 为 android.widget.Button 的元素
    appium_options = driver.find_elements(
        by=AppiumBy.CLASS_NAME, value='android.widget.Button')

    question = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR,
                                   value="new UiSelector().className(\"android.view.View\").instance(8)")
    logging.debug("-----读取屏幕内容-----")
    logging.debug(f"题目: {question.get_attribute('content-desc')}")

    # 遍历并操作这些按钮 (例如打印它们的文本)
    for i, button in enumerate(appium_options):
        try:
            # 尝试获取按钮的 text 属性
            button_text = button.get_attribute('content-desc')
            logging.debug(f"答案{i+1}: Text='{button_text}'")
        except Exception as e:
            logging.debug(f"处理按钮 {i+1} 时出错: {e}")
    logging.debug("-----读取屏幕内容完成-----")
    return question, appium_options


def get_cnt():
    """
    从屏幕上抓取当前的答题数量,可能需要适配
    """
    class_view = driver.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().className("
                                                                             "\"android.view.View\")")
    cnt = class_view[len(class_view) - 4].tag_name
    cnt = int(cnt)
    logging.debug(f">--当前答题数量: {cnt}--<")
    return cnt


def is_exited():
    """
    检查当前是否在答题界面,可能需要适配
    :return: True:在答题界面,False:不在答题界面
    """
    logging.debug("-----检查是否在答题界面-----")
    try:
        driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR,
                            value="new UiSelector().description(\"入站问答\n通过问答后才能发言噢\")")
        return True
    except Exception as e:
        logging.critical(f"发生错误: {e}")
        return False


def enter():
    """
    进入答题界面,可能需要适配
    """
    logging.debug("-----进入答题界面-----")
    try:
        driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR,
                            value="new UiSelector().description(\"入站问答\n通过问答后才能发言噢\")").click()
        sleep(4)
        driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR,
                            value="new UiSelector().description(\"开始答题\")").click()
        sleep(4)
        driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR,
                            value="new UiSelector().description(\"确定\")").click()
        sleep(4)
        return True
    except Exception as e:
        logging.critical(f"发生错误: {e}")
        return False


def GO():
    try:
        main()
    except Exception as e:
        sleep(5)
        if is_exited():
            enter()
        else:
            quit()
            logging.debug("发生错误: ", e)


if __name__ == '__main__':
    # main()
    while True:
        init()
        check_db()
        logging.debug("-----程序开始-----")
        GO()
