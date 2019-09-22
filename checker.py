def run():
    import os
    import psutil
    from win10toast import ToastNotifier
    import getpass
    port = 5000
    processes = {}

    for process in psutil.process_iter():
        try:
            process_name = process.name()
            process_id = process.pid
            owner = process.username().split("\\")[1]
            processes[process_id] = (process_name, owner)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass

    new_pid = os.getpid()
    new_process_name = processes[new_pid]

    check = [(k, v) for k, v in processes.items() if v == new_process_name]

    already_running = len(check) > 2

    if already_running:
        toaster = ToastNotifier()
        toaster.show_toast("Activity Tracker already running",
                           "Exiting...",
                           icon_path="./static/favicon.ico",
                           duration=2)
        os._exit(0)

    username = getpass.getuser()
    output = 0
    for x in range(len(username)):
        number = ord(username[x].lower()) - 96
        output += number * (x + 1)

    # return port + (output + len(username))
    return 5244
