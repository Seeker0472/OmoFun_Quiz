import sqlite3
from time import sleep
import time

while True:
    conn = sqlite3.connect('main.sqlite')
    unknown = 0
    cursor = conn.cursor()
    all_id = cursor.execute("select id from Texts").fetchall()
    for i in all_id:
        all_ans = cursor.execute("select ok from Answers where text_id=?", (i[0],)).fetchall()
        if 2 not in [x[0] for x in all_ans]:
            unknown += 1
            # print("Not_Finished")
            # return False
    # conn.commit()
    print("时间" + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    print("未知:   " + str(unknown) + '/' + str(len(all_id)))
    print("=====================================")
    conn.close()
    sleep(60)
