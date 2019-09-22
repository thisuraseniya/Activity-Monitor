def start(kill, db_path):
    from pathlib import Path
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import datetime
    import sqlite3

    def push_data(event):
        file_types = {
            'jpg': 'fa-file-image text-success',
            'png': 'fa-file-image text-success',
            'gif': 'fa-file-image text-success',
            'ico': 'fa-file-image text-success',
            'jpeg': 'fa-file-image text-success',
            'doc': 'fa-file-word text-primary',
            'docx': 'fa-file-image text-primary',
            'txt': 'fa-file-alt text-dark',
            'mp3': 'fa-file-audio text-primary',
            'wav': 'fa-file-audio text-primary',
            'flac': 'fa-file-audio text-primary',
            'wmv': 'fa-file-audio text-primary',
            'exe': 'fa-file-code text-warning',
            'js': 'fa-file-code text-warning',
            'css': 'fa-file-code text-warning',
            'html': 'fa-file-code text-warning',
            'xls': 'fa-file-excel text-success',
            'mp4': 'fa-file-video text-primary',
            'avi': 'fa-file-video text-primary',
            'flv': 'fa-file-video text-primary',
            'mkv': 'fa-file-video text-primary',
            'pdf': 'fa-file-pdf text-danger',
            'zip': 'fa-file-archive text-danger',
            'rar': 'fa-file-archive text-danger',
            '7z': 'fa-file-archive text-danger',
        }

        file_name = str(event.src_path).split("\\")[-1]
        extension = file_name.split(".")[-1].lower()
        print("EXTENSION - " + extension)
        if extension != "tmp" and not kill.isSet():
            path = str(event.src_path)
            d = datetime.datetime.now()
            date_d = str(d).split(" ")[0]
            time_t = (str(d).split(" ")[1]).split(".")[0]
            connection = sqlite3.connect(db_path)
            my_cursor = connection.cursor()

            check_query = "SELECT * FROM downloads ORDER BY id DESC LIMIT 1"
            my_cursor.execute(check_query)
            last_row = my_cursor.fetchall()

            try:
                style_class = file_types[extension]
            except KeyError:
                style_class = "fa-file text-warning"

            try:
                if last_row[0][2] != path:
                    query = "INSERT INTO downloads(file, path, d, t, style) VALUES('" + file_name + "','" + path + "','" + date_d + "','" + time_t + "','" + style_class + "')"
                    my_cursor.execute(query)
            except IndexError:
                query = "INSERT INTO downloads(file, path, d, t, style) VALUES('" + file_name + "','" + path + "','" + date_d + "','" + time_t + "','" + style_class + "')"
                my_cursor.execute(query)
            connection.commit()

    class MyHandler(FileSystemEventHandler):
        def on_created(self, event):
            push_data(event)

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(Path.home()) + "\\Downloads", recursive=True)
    observer.start()

    while not kill.isSet():
        time.sleep(5)

    observer.stop()
    observer.join()
    return

