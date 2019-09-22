import sqlite3
import time
import datetime


db_path = ""
prev_day = ""
url_dict = {}
prev_urls = {}
changed = 0


def set_db_path(path):
    global db_path, prev_day
    db_path = path
    prev_day = str(datetime.datetime.now()).split(" ")[0]


def receive_url(url):
    global url_dict, changed
    changed = 1
    if url in url_dict:
        url_dict[url] += 1
    else:
        url_dict[url] = 1


def flush_data(kill_flag):
    time_loop = 10
    global db_path, prev_day, url_dict, prev_urls, changed
    while not kill_flag.isSet():
        if time_loop % 10 == 0:
            time_loop = 10
            today = str(datetime.datetime.now()).split(" ")[0]
            if prev_day == today and changed:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                for url in url_dict:
                    time_t = str(url_dict[url])
                    browser = "any"
                    c.execute('SELECT t FROM url_data WHERE d="' + prev_day + '" and url="' + url + '"')
                    prev_time = c.fetchone()
                    if prev_time:
                        query = 'UPDATE url_data SET t=' + time_t + ' WHERE url="' + url + '" and d="' + prev_day + '"'
                    else:
                        query = "INSERT INTO url_data(url, d, t, browser) VALUES('" + url + "','" + prev_day + "'," + time_t + ",'" + browser + "')"
                    c.execute(query)
                conn.commit()
                changed = 0
            elif prev_day != today:
                prev_day = today
                url_dict = {}
                prev_urls = {}
        else:
            time_loop += 5
        time.sleep(5)


