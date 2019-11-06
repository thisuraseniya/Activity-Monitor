import datetime
import sqlite3
import pyperclip
import time
import names_gen

prev_clipboard = ""


def monitor_clipboard(kill_flag, db_path):
    while not kill_flag.isSet():
        global prev_clipboard
        current_clipboard = pyperclip.paste()
        current_clipboard = current_clipboard.replace("'", "")
        current_clipboard = current_clipboard.replace('"', "")
        if current_clipboard != prev_clipboard:
            app_name = names_gen.find_app_name()
            print("CLIPBOARD - ", current_clipboard)
            d = datetime.datetime.now()
            date_d = str(d).split(" ")[0]
            time_t = (str(d).split(" ")[1]).split('.')[0]
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            query = "INSERT INTO clipboard_monitor(d, t, content, app) VALUES('" + date_d + "','" + time_t + "','" + str(current_clipboard) + "','" + app_name[0] + "')"
            c.execute(query)
            conn.commit()
        prev_clipboard = current_clipboard
        time.sleep(1)

