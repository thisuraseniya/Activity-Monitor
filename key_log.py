import datetime
import sqlite3

prev_window_keylogger = ''
prev_app_keylogger = ''
prev_process_keylogger = ''
prev_key = ''
exclude_log = ['Explorer', 'Searchui', 'Task Switching', '', ' ']  # these are excluded apps
words = ''
words_new = ''


def start(program_name, process, window, ctrl_pressed, key=None, x=None):
    global prev_window_keylogger, prev_app_keylogger, prev_process_keylogger, prev_key, exclude_log, words, words_new

    if program_name not in exclude_log:
        if len(key) == 1:
            if ctrl_pressed:
                words += " <SHORTCUT> "
            else:
                words += key
        elif len(words) > 0:
            if key == "Key.space":
                words += " "
            elif key == "Key.backspace" or key == "Key.delete":
                if prev_key != "Key.backspace" and prev_key != "Key.delete":
                    words += " <DELETE> "
                else:
                    pass
            elif key == "Key.enter":
                words += "\n"
        # print(process, words)
        prev_key = key
        prev_window_keylogger = window
        prev_app_keylogger = program_name
        prev_process_keylogger = process

    else:
        pass

    words_new = words

    return


def push_data(db_path):
    global words, prev_window_keylogger, prev_app_keylogger
    words_c = words

    if len(words_c) > 0:
        d = datetime.datetime.now()
        date_d = str(d).split(" ")[0]
        time_t = (str(d).split(" ")[1]).split('.')[0]

        connection = sqlite3.connect(db_path)
        my_cursor = connection.cursor()

        query3 = "SELECT * FROM key_logger ORDER BY id DESC LIMIT 1"
        my_cursor.execute(query3)
        last_row = my_cursor.fetchall()

        try:
            if last_row[0][1] == prev_window_keylogger:
                prefix = '\n'
            else:
                prefix = '\n\n======== TIME - ' + time_t + ' ======== WINDOW - ' + prev_window_keylogger + ' ===========\n'
            # if last_row[0][1] == prev_window_keylogger:
            if last_row[0][2] == prev_app_keylogger:
                last_id = str(last_row[0][0])
                len_words = str(count_words(words_c) + int(last_row[0][6]))
                words_c = (last_row[0][5] + prefix + words_c).strip()
                query2 = "UPDATE key_logger SET d = '" + date_d + "', t = '" + time_t + "', content = '" + words_c + "', characters = '" + len_words + "', window = '" + prev_window_keylogger + "'  WHERE id = " + last_id + ""
            elif len(words_c) > 0:
                len_words = str(count_words(words_c))
                words_c = prefix + words_c
                query2 = "INSERT INTO key_logger(window, p_name, d, t, content, characters) VALUES('" + prev_window_keylogger + "','" + prev_app_keylogger + "','" + date_d + "','" + time_t + "','" + words_c + "','" + len_words + "')"
            else:
                query2 = "SELECT * FROM test WHERE id = 1"
        except IndexError:
            print("index error")
            prefix = '\n\n======== TIME - ' + time_t + ' ======== WINDOW - ' + prev_window_keylogger + ' ===========\n'
            len_words = str(count_words(words_c))
            words_c = prefix + words_c
            query2 = "INSERT INTO key_logger(window, p_name, d, t, content, characters) VALUES('" + prev_window_keylogger + "','" + prev_app_keylogger + "','" + date_d + "','" + time_t + "','" + words_c + "','" + len_words + "')"
        print("LOGGED - " + words_c)
        my_cursor.execute(query2)
        connection.commit()
        words = ""

    return


def count_words(sentence):
    sentence = sentence.replace('\n', ' ')
    s = sentence.strip().split(' ')
    s = [word for word in s if word != '<DELETE>' and word != '' and word != '<SHORTCUT>']
    w_count = len(s)
    return w_count


def push_data_new(db_path):
    global words, prev_window_keylogger, prev_app_keylogger, words_new
    words_c = words_new

    if len(words_c) > 0:
        d = datetime.datetime.now()
        date_d = str(d).split(" ")[0]
        time_t = (str(d).split(" ")[1]).split('.')[0]

        connection = sqlite3.connect(db_path)
        my_cursor = connection.cursor()

        try:
            if len(words_c) > 0:
                len_words = str(count_words(words_c))
                query2 = "INSERT INTO key_logger_new(window, p_name, d, t, content, characters) VALUES('" + prev_window_keylogger + "','" + prev_app_keylogger + "','" + date_d + "','" + time_t + "','" + words_c + "','" + len_words + "')"
            else:
                pass
        except Exception as e:
            print(e)
        print("LOGGED NEW - " + words_c)
        my_cursor.execute(query2)
        connection.commit()
        words_new = ""

    return
