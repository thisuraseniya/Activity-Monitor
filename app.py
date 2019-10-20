import checker
from flask import Flask, render_template, request, send_from_directory
import sqlite3
import activity_tracker
from infi.systray import SysTrayIcon
import webbrowser
import threading
import requests
import os
import stat_engine
import shutil
from winreg import *
import time
import logging
import names_gen
import psutil

# import url_grabber

try:
    import zroya
except Exception:
    pass

log = logging.getLogger('werkzeug')
log.disabled = True

absolute_path = activity_tracker.absolute_path
db_path = activity_tracker.db_path
ss_path = activity_tracker.ss_path

# ========== CHECK IF ALREADY RUNNING ================

PORT = checker.run()

# ========== CHECK FOR DATABASE ================

activity_tracker.create_database()

# ================ FLASK APP STARTS HERE ===================

isTrackerRunning = 0
refresh = 0
# PORT = random.randint(5000, 50000)
# PORT = 6000
s_PORT = str(PORT)
i = []
exclude_apps = []
options = {
    'autorun': '0',
    'eula': '0',
    'delete_30': '0',
    'autostart': '0',
    'disable_ss': '0',
    'disable_keylog': '0'
}

if activity_tracker.AUTORUN_WINDOWS == 1:
    options['autostart'] = '1'

app = Flask(__name__, static_folder=absolute_path + '/static', template_folder=absolute_path + '/templates')


@app.route('/', methods=['GET', 'POST'])
def dash():
    return render_template('dash.html', autorun=int(options['autorun']), auto_win=int(options['autostart']),
                           delete_30=int(options['delete_30']), disable_ss=int(options['disable_ss']),
                           disable_keylog=int(options['disable_keylog']), exclude=exclude_apps, port=PORT)


@app.route('/dash/<string:date>', methods=['GET', 'POST'])
def dash_with_date(date):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if len(c.execute('SELECT * FROM tracker WHERE d = "' + date + '"').fetchall()) == 0:
        no_data = 1
    else:
        no_data = 0
    return render_template('dash.html', date=date, no_data=no_data, autorun=int(options['autorun']),
                           auto_win=int(options['autostart']), delete_30=int(options['delete_30']),
                           disable_ss=int(options['disable_ss']), disable_keylog=int(options['disable_keylog']),
                           exclude=exclude_apps, port=PORT)


@app.route('/windows/<string:date>', methods=['GET', 'POST'])
def windows(date):
    global refresh
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM tracker WHERE d="' + date + '"')
    data = c.fetchall()
    return render_template('windows.html', windows=data, date=date, refresh=refresh)


@app.route('/screenshots/<string:date>', methods=['GET', 'POST'])
def screenshots(date):
    ss = stat_engine.give_screenshots(db_path, date)
    return render_template('screenshots.html', ss=ss, date=date, ss_path=ss_path)


# This fetched screenshots from Documents folder since flask's default directory is static folder
@app.route('/<path:filename>')
def screenshots_files(filename):
    return send_from_directory(ss_path, filename)


@app.route('/usage/<string:date>', methods=['GET', 'POST'])
def usage(date):
    global refresh
    apps, timeline, timeline_colors, apps_colors = stat_engine.give_usage(db_path, date)
    eye_timeline, eye_timeline_colors = stat_engine.give_eye_tracker_data(db_path, date)

    if apps:
        no_data = 0
    else:
        no_data = 1
    tot = 0
    for each in apps:
        tot += apps[each]
    return render_template('usage.html', app_usage=apps, date=date, timeline=timeline, timeline_colors=timeline_colors,
                           refresh=refresh, apps_colors=apps_colors, total_time=tot, no_data=no_data,
                           eye_timeline=eye_timeline, eye_timeline_colors=eye_timeline_colors,
                           )


@app.route('/usage/<string:date>/<int:slot>', methods=['GET', 'POST'])
def hourly_data(date, slot):
    global refresh, db_path
    apps_hour, timeline_hour, timeline_colors_hour, apps_colors_hour = stat_engine.get_hourly_data(db_path, date, slot)
    apps, timeline, timeline_colors, apps_colors = stat_engine.give_usage(db_path, date)
    eye_timeline, eye_timeline_colors = stat_engine.give_eye_tracker_data(db_path, date)

    if apps:
        no_data = 0
    else:
        no_data = 1
    tot = 0

    if len(timeline_hour) == 0:
        no_data_hourly = 1
    else:
        no_data_hourly = 0

    for each in apps:
        tot += apps[each]
    return render_template('usage.html', app_usage=apps, date=date, timeline=timeline, timeline_colors=timeline_colors,
                           refresh=refresh, apps_colors=apps_colors, total_time=tot, no_data=no_data,
                           eye_timeline=eye_timeline, eye_timeline_colors=eye_timeline_colors,
                           apps_colors_hour=apps_colors_hour,
                           timeline_colors_hour=timeline_colors_hour, timeline_hour=timeline_hour, apps_hour=apps_hour,
                           no_data_hourly=no_data_hourly, slot=slot)


@app.route('/statistics/<string:date>', methods=['GET', 'POST'])
def statistics(date):
    global refresh
    downloads = stat_engine.give_downloads(db_path, date)
    total_usage, first_app, second_app, third_app, final_browsers = stat_engine.app_stats(db_path, date)
    word_count = stat_engine.give_word_count(db_path, date)
    url_data = stat_engine.give_url_data(db_path, date)
    if total_usage == '0 seconds':
        no_data = 1
    else:
        no_data = 0
    return render_template('statistics.html', date=date, downloads=downloads, browsers=final_browsers,
                           first_app=first_app, second_app=second_app, third_app=third_app, total_usage=total_usage,
                           word_count=word_count, refresh=refresh, no_data=no_data, url_data=url_data)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/tracker/<string:command>', methods=['GET', 'POST'])
def tracker(command):
    global refresh, isTrackerRunning, AUTORUN_WITH_WINDOWS, exclude_apps
    if command == "isRunning":
        return str(activity_tracker.running)

    elif command == "start_tracker":
        if isTrackerRunning == 0:
            if options['eula'] == '1':
                activity_tracker.start()
                isTrackerRunning = 1
                return "successful"
            else:
                return "no_eula"

    elif command == "stop_tracker":
        if isTrackerRunning == 1:
            isTrackerRunning = 0
            activity_tracker.stop()
        return "successfully stopped"

    elif command == "interval":
        activity_tracker.interval = int(request.form['i']) * 60
        return str(request.form['i'])

    elif command == "delete_keystroke":
        row_id = request.form['id']
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM key_logger WHERE id=' + row_id + '')
        conn.commit()
        return 'deleted'

    elif command == "delete_all":
        try:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                try:
                    c.execute('DELETE FROM tracker')
                    c.execute('DELETE FROM key_logger')
                    c.execute('DELETE FROM downloads')
                    c.execute('DELETE FROM test')
                except Exception as e:
                    print(e)
                conn.commit()
                out = '1'
                try:
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    c.execute('vacuum')
                    conn.commit()
                except Exception as e:
                    print(e)
            else:
                out = '3'
        except Exception as e:
            out = 5
            print(e)

        try:
            if os.path.exists(ss_path):
                shutil.rmtree(ss_path)
                out += '2'
            else:
                out += '3'
        except Exception as e:
            out = 5
            print(e)

        return out

    elif command == "delete_for_date":
        date_received = request.form['date']
        try:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute('DELETE FROM tracker WHERE d = "' + date_received + '"')
                c.execute('DELETE FROM key_logger WHERE d = "' + date_received + '"')
                c.execute('DELETE FROM downloads WHERE d = "' + date_received + '"')
                c.execute('DELETE FROM test')
                conn.commit()
                out = '1'
            else:
                out = '3'
            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute('vacuum')
                conn.commit()
            except Exception as e:
                print(e)
        except Exception as e:
            out = 5
            print(e)

        try:
            if os.path.exists(ss_path + date_received):
                shutil.rmtree(ss_path + date_received)
                out += '2'
            else:
                out += '3'
        except Exception as e:
            out = 5
            print(e)

        return out

    elif command == 'refresh':
        if refresh == 0:
            refresh = 1
        else:
            refresh = 0
        return 'ok'

    elif command == 'eula_agree':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("eula", "1")')
            conn.commit()
            load_options()
            return 'successful'
        except Exception:
            conn.commit()
            return 'already'

    elif command == 'no_data':
        date = request.form['date']
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        if len(c.execute('SELECT * FROM tracker WHERE d = "' + date + '"').fetchall()) == 0:
            return '1'
        else:
            return '0'

    elif command == 'check_autostart':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("autorun", "1")')
        conn.commit()
        load_options()
        return 'done'

    elif command == 'uncheck_autostart':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("autorun", "0")')
        conn.commit()
        load_options()
        return 'done'

    elif command == 'check_autostart_windows':
        activity_tracker.add_to_startup()
        options['autostart'] = '1'
        print(options)
        return 'done'

    elif command == 'uncheck_autostart_windows':
        print("Locating the Registry Keys")
        aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
        aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, KEY_SET_VALUE)
        try:
            DeleteValue(aKey, "Activity Tracker UCSC")
            print("Successfully deleted Activity Monitor from registry")
        except (FileNotFoundError, OSError, Exception):
            pass
        CloseKey(aKey)
        options['autostart'] = '0'
        print(options)
        return 'done'

    elif command == 'check_delete_30':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("delete_30", "1")')
        conn.commit()
        load_options()
        return 'done'

    elif command == 'uncheck_delete_30':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("delete_30", "0")')
        conn.commit()
        load_options()
        return 'done'

    elif command == 'check_disable_ss':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("disable_ss", "1")')
        conn.commit()
        load_options()
        return 'done'

    elif command == 'uncheck_disable_ss':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("disable_ss", "0")')
        conn.commit()
        load_options()
        return 'done'

    elif command == 'check_disable_keylog':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("disable_keylog", "1")')
        conn.commit()
        load_options()
        return 'done'

    elif command == 'uncheck_disable_keylog':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO options ("op_name", "op_value") VALUES ("disable_keylog", "0")')
        conn.commit()
        load_options()
        return 'done'

    elif command == "delete_window_row":
        row_id = request.form['id']
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM tracker WHERE id=' + row_id + '')
        conn.commit()
        return 'deleted'

    elif command == "delete_ss":
        ss_id = request.form['id']
        path = request.form['path']
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('UPDATE tracker SET pic="no_ss" WHERE id=' + ss_id + '')
        if os.path.exists(ss_path + path):
            os.remove(ss_path + path)
        conn.commit()
        return 'deleted'

    elif command == "delete_all_ss":
        restart_after_delete = 0

        if isTrackerRunning == 1:
            restart_after_delete = 1
            requests.get("http://127.0.0.1:" + s_PORT + "/tracker/stop_tracker")

        date = request.form['date']
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('UPDATE tracker SET pic="no_ss" WHERE d="' + date + '"')
        conn.commit()

        if os.path.exists(ss_path + date):
            shutil.rmtree(ss_path + date)

        if restart_after_delete == 1:
            requests.get("http://127.0.0.1:" + s_PORT + "/tracker/start_tracker")

        return 'deleted'

    elif command == "delete_all_keystrokes":
        restart_after_delete = 0

        if isTrackerRunning == 1:
            restart_after_delete = 1
            requests.get("http://127.0.0.1:" + s_PORT + "/tracker/stop_tracker")

        date = request.form['date']
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM key_logger WHERE d="' + date + '"')
        conn.commit()

        if restart_after_delete == 1:
            requests.get("http://127.0.0.1:" + s_PORT + "/tracker/start_tracker")

        return 'deleted'

    elif command == "add_exclude_app":
        app_rec = request.form['app'].lower()
        if app_rec not in exclude_apps:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO exclude_apps ("app_name") VALUES ("' + app_rec + '")')
            conn.commit()
            load_options()
            return 'excluded'
        else:
            return 'already'

    elif command == "remove_exclude_app":
        app_rec = request.form['app'].lower()
        print(app_rec)
        if app_rec in exclude_apps:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('DELETE FROM exclude_apps WHERE app_name ="' + app_rec + '"')
            conn.commit()
            load_options()
            return 'removed'
        else:
            return 'already'

    elif command == "get_process_list":
        processes = {}
        ignore = ['msmpeng.exe', 'ctfmon.exe', 'svchost.exe', 'runtimebroker.exe', 'smartscreen.exe', 'registry']
        for proc in psutil.process_iter():
            try:
                proc.username()
                name = proc.name().lower()
                ram = proc.memory_info().vms / 1024 / 1024
                if ram > 1 and name not in ignore and name not in exclude_apps:
                    if name not in processes:
                        processes[name] = ram
                    elif name in processes:
                        if processes[name] < ram:
                            processes[name] = ram
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        process_list = [x[0] for x in sorted(processes.items(), key=lambda kv: kv[1], reverse=True)]

        output = '<div class="list-group">'
        for p in process_list:
            output += '<button type="button" class="list-group-item list-group-item-action justify-content-between align-items-center" style="cursor: pointer" onClick="exclude_from_list(this)" process="' + p + '">' + p + '</button>'
        output += '</div>'

        return output
    elif command == "url":
        url_rec = request.form['url']
        youtube_paused = request.form['paused']
        has_youtube = request.form['video']
        activity_tracker.pass_to_url_grabber(url_rec)
        activity_tracker.pass_to_video_monitor(has_youtube)
        return 'thanks'

    elif command == "get_hourly_stat":
        slot = int(request.form['slot'])
        date = request.form['date']
        stat_engine.get_hourly_data(db_path, date, slot)
        print(slot, date)
        return 'thanks'

    else:
        return "invalid command"


@app.route('/keystrokes/<string:date>', methods=['GET', 'POST'])
def keystrokes(date):
    global refresh
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM key_logger WHERE d="' + date + '"')
    data = c.fetchall()
    return render_template('keystrokes.html', key_data=data, date=date, refresh=refresh)


@app.route('/EULA', methods=['GET', 'POST'])
def eula():
    if options['eula'] == '1':
        agree = 1
    else:
        agree = 0
    return render_template('eula.html', agreed=agree, port=s_PORT)


@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


# ================= FLASK APP ENDS HERE ======================


def load_options():
    global options, exclude_apps
    print('')
    print('====== LOADING OPTIONS')
    global options
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    all_ops = c.execute('SELECT op_name, op_value FROM options').fetchall()
    ex_apps = c.execute('SELECT app_name FROM exclude_apps').fetchall()
    conn.commit()

    for op in all_ops:
        options[op[0]] = op[1]

    exclude_apps = []
    for ex_app in ex_apps:
        if ex_app[0] not in exclude_apps:
            exclude_apps.append(ex_app[0])

    print(options)
    print(exclude_apps)
    activity_tracker.get_options(options)
    names_gen.get_exclude_apps(exclude_apps)
    print('====== LOADING COMPLETE')
    return


def open_dashboard(x):
    notify("Opening dashboard. Please wait...",
           "Your browser will open automatically.\n( If it does not, open your browser manually and go to\nhttp://localhost:" + s_PORT + " )",
           0)
    webbrowser.get('windows-default').open('http://localhost:' + s_PORT)
    return


def on_quit(systray):
    requests.get("http://127.0.0.1:" + s_PORT + "/shutdown")
    threading.Thread(target=activity_tracker.stop, args=()).start()
    time.sleep(5)
    threading.Thread(target=q, args=()).start()
    return


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def q():
    global i
    print("Quitting")
    time.sleep(2)
    for nid in i:
        zroya.hide(nid)
    os._exit(0)


def start_tracker(x):
    global isTrackerRunning, absolute_path
    if isTrackerRunning == 0:
        requests.get("http://127.0.0.1:" + s_PORT + "/tracker/start_tracker")
        time.sleep(0.5)
        if isTrackerRunning:
            notify("Tracker started successfully", "Tracking your activities...")
        else:
            if options['eula'] == '0' or options['eula'] is None:
                notify("Please read and accept the Terms and Conditions", "Wait for your browser window to open...")
                webbrowser.get('windows-default').open('http://127.0.0.1:' + s_PORT + '/EULA')
            else:
                notify("Tracker failed to start", "Please try again later")
    else:
        notify("Tracker already running", "Try 'Stop Tracker' instead")
    return


def stop_tracker(x):
    global isTrackerRunning
    if isTrackerRunning == 1:
        requests.get("http://127.0.0.1:" + s_PORT + "/tracker/stop_tracker")
        notify("Tracker stopped successfully", "Until next time...")
    else:
        notify("Tracker already stopped", "Try 'Start Tracker' instead")
    return


def notify(first, second, action=1):
    global i
    notifications = 0
    try:
        notifications = zroya.init("Activity Monitor", "Professional Practice", "Activity Monitor", "KeyLogger", "v1.0")
    except Exception:
        pass

    if notifications != 0:
        template = zroya.Template(zroya.TemplateType.ImageAndText4)
        template.setFirstLine(first)
        template.setSecondLine(second)
        try:
            template.setImage(absolute_path + "/static/icon.png")
        except FileNotFoundError:
            print("Image not found")
            print("PWD - " + absolute_path)
            print("PIC PATH - " + absolute_path + "/static/icon.png")
        template.setExpiration(30000)

        if action:
            template.addAction("Open Dashboard")
        i.append(zroya.show(template, on_action=on_action))
    return


def on_action(notification_id, action_id):
    open_dashboard(notification_id)
    return


# =============== MAIN PROGRAM ===================

menu_options = (
    ("Open Dashboard", absolute_path + "/static/dash.ico", open_dashboard), ("Start Tracker", None, start_tracker),
    ("Stop Tracker", None, stop_tracker))
tray = SysTrayIcon(absolute_path + "/static/favicon.ico", "Activity Monitor", menu_options, on_quit)
tray.start()
load_options()

try:
    if options['delete_30'] == '1':
        print('')
        print('====== CLEANING OLDER RECORDS')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM key_logger WHERE d <= date('now','-30 day')")
        c.execute("DELETE FROM tracker WHERE d <= date('now','-30 day')")
        c.execute("DELETE FROM downloads WHERE d <= date('now','-30 day')")
        conn.commit()
        now = time.time()
        before_30 = now - 30 * 86400
        if os.path.exists(ss_path):
            for f in os.listdir(ss_path):
                if os.stat(os.path.join(ss_path, f)).st_mtime < before_30:
                    shutil.rmtree(ss_path + f)
                    print("Deleting folder - " + f)
        print('====== CLEANING COMPLETED')
        print('')

    if options['autorun'] == '1':
        if options['eula'] == '0' or options['eula'] is None:
            notify("Monitoring did not start automatically",
                   "Please open the Dashboard and start manually\n(Reason - EULA not accepted)", 0)
        else:
            activity_tracker.start()
            isTrackerRunning = 1
            notify("Activity Monitor successfully started", "Minimized to system tray", 0)

except Exception as e:
    print(e)
    notify("Activity Monitor successfully started", "Minimized to system tray", 0)

time.sleep(1)

if __name__ == '__main__':
    app.run(port=PORT)
