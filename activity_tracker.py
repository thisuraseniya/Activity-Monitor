import sqlite3
import win32gui
import datetime
import time
import pyautogui
from pynput import mouse, keyboard
import threading
import os
from winreg import *
import sys
import names_gen
import storage_watcher
import key_log
import ctypes
import url_grabber_new
# import url_grabber
import eye_tracker

hllDll = ctypes.WinDLL("User32.dll")
VK_CAPITAL = 0x14
AUTORUN_WINDOWS = 0
options = {}

# =============== Check Registry =================

Registry = ConnectRegistry(None, HKEY_CURRENT_USER)
RawKey = OpenKey(Registry, "SOFTWARE\Microsoft\Windows\CurrentVersion\Run")


# this will add the file to the startup registry key
def add_to_startup():
    # fp = os.path.dirname(os.path.realpath(__file__))
    file_name = sys.argv[0].split('/')[-1]
    # new_file_path = fp + '\\' + file_name
    new_file_path = file_name
    key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER, key_value, 0, KEY_ALL_ACCESS)
    SetValueEx(key2change, 'Activity Tracker UCSC', 0, REG_SZ, new_file_path)
    print("Added to registry - " + new_file_path)
    return new_file_path


try:
    print('====== RESOLVING APP PATH')
    i = 0
    while 1:
        name, path, t = EnumValue(RawKey, i)
        if name == "Activity Tracker UCSC":
            print("Path found in registry - " + path)
            AUTORUN_WINDOWS = 1
            break
        i += 1
except OSError:
    file_name = sys.argv[0].split('/')[-1]
    path = file_name


path = path.replace('"', "")
parts = path.split("\\")
if len(parts) < 2:
    parts = path.split("/")
parts.pop()
absolute_path = "/".join(parts)
print("Absolute path - " + absolute_path)
print('====== COMPLETE')


# ============ End Check Registry ===============

w = win32gui

prev_prog = ''
prev_window = ''
prev_window_keylogger = ''
prev_window_track = ''
prev_process_keylogger = ''
today = ''
logger = []
prev_key = ''
shift_pressed = 0
ctrl_pressed = 0
kill = 0
m_listener = ''
k_listener = ''
interval = 180
running = 0
characters = {'`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', '[': '{', ']': '}', ';': ':', ',': '<', '.': '>', '/': '?'}
exclude_processes = ['searchui.exe', 'lockapp.exe']
db_path = os.path.expanduser("~") + "\\Documents\\Activity Monitor\\Database\\tracker.db"
ss_path = os.path.expanduser("~") + "\\Documents\\Activity Monitor\\Screenshots\\"


# Create database, establish connection and create tables
def create_database():
    global db_path
    if not os.path.exists(os.path.expanduser("~") + "\\Documents\\Activity Monitor\\Database"):
        os.makedirs(os.path.expanduser("~") + "\\Documents\\Activity Monitor\\Database")

    if not os.path.exists(os.path.expanduser("~") + "\\Documents\\Activity Monitor\\Database\\tracker.db"):
        print("")
        print("====== CREATING DATABASE")
        connection_ini = sqlite3.connect(db_path)
        my_cursor_ini = connection_ini.cursor()
        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS tracker ( id INTEGER PRIMARY KEY, app TEXT, process TEXT,
            d TEXT,
            t TEXT,
            pic TEXT,
            full_window TEXT)''')

        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS key_logger ( id INTEGER PRIMARY KEY, window TEXT, p_name TEXT,
            d TEXT,
            t TEXT,
            content TEXT, characters TEXT)''')

        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS downloads ( id INTEGER PRIMARY KEY, file TEXT, path TEXT,
            d TEXT,
            t TEXT, 
            style TEXT )''')

        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS test ( id INTEGER PRIMARY KEY, data_in TEXT )''')
        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS options ( op_name TEXT PRIMARY KEY, op_value TEXT )''')
        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS exclude_apps ( app_name TEXT PRIMARY KEY )''')
        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS eye_tracker ( id INTEGER PRIMARY KEY, d TEXT, t TEXT, no_video INTEGER, face INTEGER, eyes INTEGER)''')
        my_cursor_ini.execute('''CREATE TABLE IF NOT EXISTS url_data ( id INTEGER PRIMARY KEY, url TEXT, start_t TEXT, end_t TEXT, t INTEGER, d TEXT)''')
        connection_ini.commit()
        print("====== CREATING DATABASE COMPLETE")
    return


# This module keeps on monitoring per 3 minutes
def persistent(kill_flag):
    global interval, db_path, exclude_processes
    time_loop = 5
    while not kill_flag.isSet():
        if time_loop % interval == 0:
            time_loop = 5
            connection = sqlite3.connect(db_path)
            my_cursor = connection.cursor()
            program_name, process, window = names_gen.find_app_name()

            if program_name == '' or program_name == 'Task Switching':
                program_name = "Explorer"

            if program_name != '' and window != '' and process not in exclude_processes:
                print("THREAD - " + program_name)
                d = datetime.datetime.now()
                date_d = str(d).split(" ")[0]
                time_t = (str(d).split(" ")[1]).split(".")[0]

                if options['disable_ss'] == '0':
                    pic_name = generate_name()
                    threading.Thread(name="ss thread by persistent", target=screen_shot, args=(pic_name,)).start()
                    pic_name = today + "/" + pic_name
                elif options['disable_ss'] == '1':
                    pic_name = 'no_ss'

                query = "INSERT INTO tracker(app, process, d, t, pic, full_window) VALUES('" + program_name + "','" + process + "','" + date_d + "','" + time_t + "','" + pic_name + "','" + str(window) + "')"
                my_cursor.execute(query)
                connection.commit()

            threading.Thread(name="Persistent key logger push", target=key_log.push_data, args=(db_path,)).start()
        else:
            time_loop += 5
        time.sleep(5)
    return


# take screenshots
def screen_shot(ss_name):
    global ss_path, today
    try:
        pyautogui.screenshot().save(ss_path + today + "/" + ss_name)
    except Exception as e:
        print(e)
    return


# Actual tracking function
# def track(x=0, y=0):

def track():
    try:
        global prev_window, exclude_processes, prev_window_track

        connection = sqlite3.connect(db_path)
        my_cursor = connection.cursor()

        program_name, process, window = names_gen.find_app_name()
        prev_window = window

        d = datetime.datetime.now()
        date_d = str(d).split(" ")[0]
        time_t = (str(d).split(" ")[1]).split(".")[0]

        if program_name == '' or program_name == 'Task Switching':
            program_name = "Explorer"

        if program_name != '' and window != '' and program_name != "Shellexperiencehost" and process not in exclude_processes and prev_window_track != window:  # ignore shell experience host

            print("PROGRAM - " + program_name)

            if options['disable_ss'] == '0':
                pic_name = generate_name()
                threading.Thread(name="ss thread by persistent", target=screen_shot, args=(pic_name,)).start()
                pic_name = today + "/" + pic_name
            elif options['disable_ss'] == '1':
                pic_name = 'no_ss'

            query = "INSERT INTO tracker(app, process, d, t, pic, full_window) VALUES('" + program_name + "','" + process + "','" + date_d + "','" + time_t + "','" + pic_name + "','" + str(window) + "')"
            my_cursor.execute(query)
            prev_window_track = window
        prev_window = window
        connection.commit()

    except Exception as e:
        print(e)
    return


# compare and only initialize functions when window changed, otherwise log keys
def compare_windows(key=None, x=None):
    global prev_window, db_path, options
    window = w.GetWindowText(w.GetForegroundWindow())
    window = window.replace("'", "")
    window = window.replace('"', '')

    if prev_window != window:
        # prev_window = window
        if options['disable_keylog'] == '0':
            threading.Thread(name="push data key logger", target=key_log.push_data, args=(db_path,)).start()

        threading.Thread(name="track thread", target=track, args=()).start()

    else:
        pass
    return


# generate names for screenshots
def generate_name():
    g_name = str(datetime.datetime.now()).replace('.', '')
    g_name = g_name.replace(':', '')
    g_name = g_name.replace(' ', '')
    g_name += ".png"
    return g_name


# Create a folder with today's name for screenshots
def folder(kill_flag):
    global today, prev_window_track
    previous_today = ''

    while not kill_flag.isSet():
        date_time = datetime.datetime.now()
        today = date_time.strftime("%Y-%m-%d")
        now_time = date_time.strftime("%H-%M-%S")
        if now_time == '23-59-58':
            prev_window_track = ''
            threading.Thread(name="track thread", target=track, args=()).start()
        if today != previous_today:
            if not os.path.exists(ss_path + today):
                os.makedirs(ss_path + today)
                prev_window_track = ''
                threading.Thread(name="track thread", target=track, args=()).start()
        previous_today = today
        time.sleep(1)
    return


# Mouse on move
def on_move(x, y):
    compare_windows()
    return


# Mouse on click
def on_click(x, y, button, pressed):
    compare_windows()
    return


# Mouse on scroll
def on_scroll(x, y, dx, dy):
    compare_windows()
    return


# Keyboard button on release
def on_release(x):
    global shift_pressed, characters, ctrl_pressed, db_path, options, exclude_processes

    compare_windows()
    program_name, process, window = names_gen.find_app_name()

    if options['disable_keylog'] == '0' and process != 'Excluded App':
        key_released = str(x).replace("'", "")

        if key_released == 'Key.shift' or key_released == 'Key.shift_r' or key_released == 'Key.shift_l':
            shift_pressed = 0
        elif key_released == 'Key.ctrl' or key_released == 'Key.ctrl_r' or key_released == 'Key.ctrl_l':
            ctrl_pressed = 0

        if shift_pressed == 1:
            try:
                key_released = characters[key_released]
            except KeyError:
                key_released = key_released.capitalize()

        if hllDll.GetKeyState(VK_CAPITAL):
            key_released = key_released.capitalize()

        threading.Thread(name="Keylogger thread", target=key_log.start, args=(program_name, process, window, ctrl_pressed, key_released,)).start()

    return


# Keyboard on press
def on_press(x):
    global shift_pressed, ctrl_pressed
    key_pressed = str(x).replace("'", "")
    if key_pressed == 'Key.shift' or key_pressed == 'Key.shift_r' or key_pressed == 'Key.shift_l':
        shift_pressed = 1
    elif key_pressed == "Key.ctrl_l" or key_pressed == "Key.ctrl_r" or key_pressed == "Key.ctrl":
        ctrl_pressed = 1
    # compare_windows()
    return


# Keyboard listener
def kb_listen():
    global k_listener
    k_listener = keyboard.Listener(name="kb listener thread", on_press=on_press, on_release=on_release)
    k_listener.start()
    return


# Mouse listener
def mouse_listen():
    global m_listener
    m_listener = mouse.Listener(name="mouse listener thread", on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    m_listener.start()
    return


def per_sec_track(kill_flag):
    while not kill_flag.isSet():
        compare_windows()
        time.sleep(1)
    return


def get_options(ops_rec):
    global options
    options = ops_rec
    return


def pass_to_url_grabber(url_rec):
    global running
    if running:
        # url_grabber.receive_url(url_rec)
        url_grabber_new.receive_url(url_rec)
    return


# Start App
def start():
    global kill, running, db_path
    kill = threading.Event()
    # url_grabber.set_db_path(db_path)
    url_grabber_new.set_db_path(db_path)
    print("App Started\n=====================================")
    threading.Thread(name="folder thread", target=folder, args=(kill,)).start()
    threading.Thread(name="persistent thread", target=persistent, args=(kill,)).start()
    threading.Thread(name="storage watcher", target=storage_watcher.start, args=(kill, db_path,)).start()
    threading.Thread(name="kb thread", target=kb_listen, args=()).start()
    # threading.Thread(name="mouse thread", target=mouse_listen, args=()).start()
    threading.Thread(name="per second tracker", target=per_sec_track, args=(kill,)).start()
    threading.Thread(name="url flush thread", target=url_grabber_new.flush_data, args=(kill,)).start()
    threading.Thread(name="eye tracker thread", target=eye_tracker.timed_runs, args=(kill, db_path)).start()
    running = 1
    return


# stop all threads
def stop():
    global kill, running, db_path, prev_window_track
    try:
        print("Trying to stop Activity Monitor")
        prev_window_track = ''
        threading.Thread(name="END track thread", target=track, args=()).start()
        threading.Thread(name="END key logger push", target=key_log.push_data, args=(db_path,)).start()
        # m_listener.stop()
        kill.set()

        if running == 1:
            k_listener.stop()

        running = 0
        time.sleep(2)
        print("All systems Exit")
    except Exception:
        print("Activity Monitor Already Stopped")
    return


