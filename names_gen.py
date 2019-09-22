import win32process
import win32con
import win32api
import win32gui

exclude_apps = []


def get_exclude_apps(apps_rec):
    global exclude_apps
    exclude_apps = apps_rec
    return


def find_app_name():
    global exclude_apps

    substitute_names = {
        'Msedge': 'Edge (Chromium)',
        'Picasaphotoviewer': 'Picasa',
        'Pycharm64': 'PyCharm',
        'Startmenuexperiencehost': 'Explorer'
    }

    window_object = win32gui.GetForegroundWindow()
    window_original = win32gui.GetWindowText(window_object)
    window_original = window_original.replace("'", "")
    window_original = window_original.replace('"', '')

    try:
        thread_pid, process_pid = win32process.GetWindowThreadProcessId(window_object)
        process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process_pid)
        process_name = win32process.GetModuleFileNameEx(process, 0)
        process_name = process_name.split("\\")[-1].lower()
        app_name = process_name.split(".exe")[0].title()

    except Exception as e:
        app_name = window_original.split("- ")[-1].title()
        process_name = (app_name.replace(" ", "_") + ".exe").lower()
        # app_name = "Task Manager"

    if process_name == "applicationframehost.exe":
        app_name = window_original.split("- ")[-1].title()

    if app_name in substitute_names:
        app_name = substitute_names[app_name]

    if process_name.lower() in exclude_apps:
        process_name = "Excluded App"
        app_name = "Excluded App"
        window_original = "Excluded App"

    return app_name, process_name, window_original



