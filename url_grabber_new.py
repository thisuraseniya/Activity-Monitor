import sqlite3
import time
from datetime import datetime, timedelta

db_path = ""
prev_day = ""
url_list = []
prev_urls = []
changed = 0
FMT = '%H:%M:%S'


def set_db_path(path):
    global db_path, prev_day
    db_path = path
    prev_day = str(datetime.now()).split(" ")[0]


def receive_url(url):
    global url_list, changed, FMT
    changed = 1
    t = str(datetime.now()).split(" ")[1].split(".")[0]
    try:
        diff = str(datetime.strptime(t, FMT) - datetime.strptime(url_list[-1][2], FMT))  # now time - last time
        dt = datetime.strptime(str(diff), FMT)  # convert to H-M-S
        delta = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
        diff_last = int(delta.total_seconds())
        if url_list[-1][0] == url and diff_last < 60:
            diff_new = str(datetime.strptime(t, FMT) - datetime.strptime(url_list[-1][1], FMT))  # now time - last time
            dt_new = datetime.strptime(str(diff_new), FMT)  # convert to H-M-S
            delta_new = timedelta(hours=dt_new.hour, minutes=dt_new.minute, seconds=dt_new.second)  # covert to time delta
            diff_last = int(delta_new.total_seconds())
            url_list[-1][3] = diff_last
            url_list[-1][2] = t
        else:
            url_list.append([url, t, t, 0, prev_day])
    except IndexError:
        url_list.append([url, t, t, 0, prev_day])


def flush_data(kill_flag):
    time_loop = 10
    global db_path, prev_day, url_list, prev_urls, changed
    while not kill_flag.isSet():
        if time_loop % 20 == 0:
            time_loop = 10
            today = str(datetime.now()).split(" ")[0]
            if prev_day == today and changed:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                for record in url_list:
                    url = record[0]
                    start_t = record[1]
                    end_t = record[2]
                    t = str(record[3])
                    d = record[4]
                    if int(t) < 2:
                        continue
                    query = "INSERT INTO url_data(url, start_t, end_t, t, d) VALUES('" + url + "','" + start_t + "','" + end_t + "'," + t + ",'" + d +"')"
                    c.execute(query)
                conn.commit()
                changed = 0
                url_list = []
            elif prev_day != today:
                prev_day = today
                url_list = []
                prev_urls = []
        else:
            time_loop += 5
        time.sleep(5)


