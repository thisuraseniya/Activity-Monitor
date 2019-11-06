import psutil
import time
import datetime
import sqlite3


def get_stats():
    network = psutil.net_io_counters(pernic=True)

    try:
        wifi_down = network["Wi-Fi"][1] / (1024 * 1024)
        ethernet_down = network["Ethernet"][1] / (1024 * 1024)
        download = wifi_down + ethernet_down
    except Exception:
        download = 0

    try:
        wifi_up = network["Wi-Fi"][0] / (1024 * 1024)
        ethernet_up = network["Ethernet"][0] / (1024 * 1024)
        upload = wifi_up + ethernet_up
    except Exception:
        upload = 0

    return download, upload


def push_data(kill_flag, db_path):
    start_download, start_upload = get_stats()
    while not kill_flag.isSet():
        time.sleep(15)
        current_download, current_upload = get_stats()
        download_data = current_download - start_download
        upload_data = current_upload - start_upload
        d = datetime.datetime.now()
        date_d = str(d).split(" ")[0]

        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('SELECT * FROM network_monitor WHERE d="' + date_d + '"')
            prev_record = c.fetchall()

            if len(prev_record) == 0:
                query2 = "INSERT INTO network_monitor (d, download, upload) VALUES ('" + date_d + "', " + str(
                    download_data) + ", " + str(upload_data) + ")"
            else:
                query2 = "UPDATE network_monitor SET download=" + str(
                    download_data + float(prev_record[0][2])) + ", upload=" + str(
                    upload_data + float(prev_record[0][3])) + " WHERE d='" + date_d + "'"

            c.execute(query2)
            conn.commit()
            start_download, start_upload = current_download, current_upload

        except Exception as e:
            print(e)

    return
