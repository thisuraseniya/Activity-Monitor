import sqlite3
import datetime

browsers = {}
browsers_real = {}


def give_usage(db_path, date):
    global browsers, browsers_real
    browsers = {'Opera': [], 'Chrome': [], 'Microsoft Edge': [], 'Iexplore': [], 'Firefox': [], 'Safari': [],
                'Edge (Chromium)': []}
    browsers_real = {'Opera': [], 'Chrome': [], 'Microsoft Edge': [], 'Iexplore': [], 'Firefox': [], 'Safari': [],
                     'Edge (Chromium)': []}

    colors = [
        '#1f77b4', '#2ca02c', '#d62728', '#ff7f0e', '#9467bd', '#e377c2', '#bcbd22', '#17becf', '#8c564b', '#9edae5',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#7f7f7f'
    ]

    fmt = '%H:%M:%S'
    idle_time = datetime.timedelta(seconds=185)
    today = datetime.date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM tracker WHERE d="' + date + '" ORDER BY t')
    data = c.fetchall()

    c.execute('SELECT DISTINCT app FROM tracker WHERE d="' + date + '"')
    applications = c.fetchall()
    # create dictionary
    apps = {}
    apps_colors = {}
    timeline = []
    timeline_colors = []

    for row in applications:
        app_name = row[0].split(' - ')[0]
        apps[app_name] = 0
        apps_colors['Inactive'] = '#eeeeee'
        apps_colors['No Data'] = '#ffffff'
        if app_name not in apps_colors:
            apps_colors[app_name] = colors[0]
            colors.append(colors.pop(0))

    try:
        time_large = data[0][4].split('.')[0]  # get time of 1st record
        time_small = "00:00:00"  # midnight
        diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small, fmt)  # big - small
        dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
        delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
        midnight_minutes = delta.total_seconds() / 60  # convert to seconds then to minutes

        if midnight_minutes > 3.1:
            timeline.append(["Inactive", midnight_minutes])
        else:
            timeline.append([data[0][1], midnight_minutes])

    except (ValueError, IndexError):
        pass

    x = 1
    while x < len(data):
        try:
            time_large = data[x][4].split('.')[0]  # get time of 2nd record
            time_small = data[x - 1][4].split('.')[0]  # get time of 1st record
            diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small,
                                                                                            fmt)  # big - small
            dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
            delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
            usage_minutes = delta.total_seconds() / 60  # convert to seconds then to minutes
        except ValueError:
            print('ValueError - Error calculating - Probably system time was changed')
            print("PREVIOUS - " + str(data[x - 1]))
            print("THIS - " + str(data[x]))
            pass

        if diff > idle_time:
            try:
                if timeline[-1][0] == "Inactive":
                    timeline[-1][1] += usage_minutes
                else:
                    timeline.append(["Inactive", usage_minutes])
            except IndexError:
                timeline.append(["Inactive", usage_minutes])

        else:
            try:
                apps[data[x - 1][1]] += usage_minutes
                # apps[data[x - 1][1].split(' - ')[0]] += usage_minutes  ======= this was here
                # if timeline[-1][0] == data[x - 1][1].split(' - ')[0]: ========== this also
                if timeline[-1][0] == data[x - 1][1]:
                    timeline[-1][1] += usage_minutes
                    try:
                        if data[x - 1][1] in browsers:
                            mid = data[x - 1][6].split('-')
                            if len(mid) > 1:
                                window = '-'.join(mid[:-1])
                            else:
                                window = mid[0]

                            if window not in browsers[data[x - 1][1]]:
                                browsers[data[x - 1][1]].append(window)
                                browsers_real[data[x - 1][1]].append(data[x - 1][4] + '  |  ' + window)

                    except Exception as e:
                        print(e)
                else:
                    # timeline.append([data[x - 1][1].split(' - ')[0], usage_minutes])  ========== this tooo
                    timeline.append([data[x - 1][1], usage_minutes])
                    try:
                        if data[x - 1][1] in browsers:
                            mid = data[x - 1][6].split('-')
                            if len(mid) > 1:
                                window = '-'.join(mid[:-1])
                            else:
                                window = mid[0]
                            if window not in browsers[data[x - 1][1]]:
                                browsers[data[x - 1][1]].append(window)
                                browsers_real[data[x - 1][1]].append(data[x - 1][4] + '  |  ' + window)
                    except Exception as e:
                        print(e)
            except ValueError:
                print('ValueError - Error calculating - Probably system time was changed')
                pass
            except IndexError:
                # timeline.append([data[x - 1][1].split(' - ')[0], usage_minutes]) =========== this as well
                timeline.append([data[x - 1][1], usage_minutes])

        x += 1

    try:
        time_large = "23:59:59"  # get time of 2nd record
        time_small = data[-1][4].split('.')[0]  # get time of last record
        diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small, fmt)  # big - small
        dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
        delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
        no_data_time = delta.total_seconds() / 60  # convert to seconds then to minutes

        if no_data_time > 3:
            if today == data[-1][3]:
                timeline.append(["No Data", no_data_time])
            else:
                timeline.append(["Inactive", no_data_time])

    except (ValueError, IndexError):
        print('ValueError - Error calculating - Probably system time was changed')
        pass

    for record in timeline:
        timeline_colors.append(apps_colors[record[0]])

    return apps, timeline, timeline_colors, apps_colors


def give_downloads(db_path, date):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM downloads WHERE d="' + date + '"')
    data = c.fetchall()
    return data


# def give_network_usage():
#     stat = psutil.net_io_counters()
#     downloads = round(stat.bytes_recv/1024/1024, 2)
#     uploads = round(stat.bytes_sent/1024/1024, 2)
#     return downloads, uploads


def app_stats(db_path, date):
    apps, timeline, timeline_colors, apps_colors = give_usage(db_path, date)
    apps_copy = apps
    global browsers_real
    total_usage = 0
    for app in apps:
        total_usage += apps[app]

    try:
        first = max(apps, key=apps.get)
        first_app = [first, convert_time(apps_copy[first], 1)]
        apps[first] = -1
        second = max(apps, key=apps.get)
        second_app = [second, convert_time(apps_copy[second], 1)]
        apps[second] = -1
        third = max(apps, key=apps.get)
        third_app = [third, convert_time(apps_copy[third], 1)]
    except ValueError:
        first_app = ""
        second_app = ""
        third_app = ""

    final_browsers = {}
    for browser in browsers_real:
        if len(browsers_real[browser]) != 0:
            final_browsers[browser] = browsers_real[browser]
        else:
            pass

    final_time = convert_time(total_usage)
    return final_time, first_app, second_app, third_app, final_browsers


def give_word_count(db_path, date):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM key_logger WHERE d="' + date + '"')
    data = c.fetchall()
    words = 0

    for row in data:
        words += int(row[6])

    return words


def convert_time(minutes, t=0):
    usage = str(datetime.timedelta(minutes=minutes)).split(':')
    hours = usage[0]
    minutes = usage[1]
    seconds = str(round(float(usage[2]), 0)).split('.')[0]
    final_time = ''
    if hours != '00' and hours != '0':
        if hours == '1':
            final_time += str(hours) + " hour\n"
        else:
            final_time += str(hours) + " hours\n"
    if minutes != '00':
        if minutes == '1' or minutes == '01':
            final_time += str(minutes) + " minute\n"
        else:
            final_time += str(minutes) + " minutes\n"
    if (minutes == '00' and (hours == '0' or hours == '00')) or t == 0:
        if seconds == '1' or seconds == '01':
            final_time += str(seconds) + " second"
        else:
            final_time += str(seconds) + " seconds"

    return final_time


def give_screenshots(db_path, date):
    screenshots = {}
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM tracker WHERE d="' + date + '" AND pic != "no_ss"')
    data = c.fetchall()
    for row in data:
        app = row[1].replace(".", "_")
        app = app.replace(" ", "_")
        if app in screenshots:
            screenshots[app].append(row)
        else:
            screenshots[app] = [row]

    return screenshots


def give_url_data(db_path, date):
    url = {}
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT url, t, start_t, end_t FROM url_data WHERE d="' + date + '" ORDER BY t DESC')
    data = c.fetchall()
    for row in data:
        if row[0] in url:
            url[row[0]] += row[1]
        else:
            url[row[0]] = row[1]
    return url


def give_eye_tracker_data(db_path, date):
    fmt = '%H:%M:%S'
    today = datetime.date.today().strftime("%Y-%m-%d")
    idle_time = datetime.timedelta(seconds=188)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM eye_tracker WHERE d="' + date + '" ORDER BY t')
    data = c.fetchall()

    timeline = []
    timeline_colors = []

    try:
        time_large = data[0][2].split('.')[0]  # get time of 1st record
        time_small = "00:00:00"  # midnight
        diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small, fmt)  # big - small
        dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
        delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
        midnight_minutes = delta.total_seconds() / 60  # convert to seconds then to minutes

        if midnight_minutes > 3.1:
            timeline.append(["Inactive", midnight_minutes])
        else:
            timeline.append([data[0][1], midnight_minutes])

    except (ValueError, IndexError):
        pass

    x = 1
    while x < len(data):
        try:
            time_large = data[x][2].split('.')[0]  # get time of 2nd record
            time_small = data[x - 1][2].split('.')[0]  # get time of 1st record
            diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small,
                                                                                            fmt)  # big - small
            dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
            delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
            usage_minutes = delta.total_seconds() / 60  # convert to seconds then to minutes
        except ValueError:
            print('ValueError - Error calculating - Probably system time was changed')
            print("PREVIOUS - " + str(data[x - 1]))
            print("THIS - " + str(data[x]))
            pass

        if diff > idle_time:
            try:
                if timeline[-1][0] == "Inactive":
                    timeline[-1][1] += usage_minutes
                else:
                    timeline.append(["Inactive", usage_minutes])
            except IndexError:
                timeline.append(["Inactive", usage_minutes])

        else:
            try:
                if data[x - 1][3] == 0:
                    if data[x - 1][5] == 1:
                        if timeline[-1][0] == "Active":
                            timeline[-1][1] += usage_minutes
                        else:
                            timeline.append(["Active", usage_minutes])
                    elif data[x - 1][4] == 1:
                        if timeline[-1][0] == "Active":
                            timeline[-1][1] += usage_minutes
                        else:
                            timeline.append(["Active", usage_minutes])
                    else:
                        timeline.append(["Inactive", usage_minutes])
                elif data[x - 1][3] == 1:
                    if timeline[-1][0] == "Camera not found / in use":
                        timeline[-1][1] += usage_minutes
                    else:
                        timeline.append(["Camera not found / in use", usage_minutes])
            except ValueError:
                print('ValueError - Error calculating - Probably system time was changed')
                pass
            except IndexError:
                timeline.append([data[x - 1][1], usage_minutes])

        x += 1

    try:
        time_large = "23:59:59"  # get time of 2nd record
        time_small = data[-1][2].split('.')[0]  # get time of last record
        diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small, fmt)  # big - small
        dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
        delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
        no_data_time = delta.total_seconds() / 60  # convert to seconds then to minutes

        if no_data_time > 3:
            if today == data[-1][1]:
                timeline.append(["No Data", no_data_time])
            else:
                timeline.append(["Inactive", no_data_time])

    except (ValueError, IndexError):
        print('ValueError - Error calculating - Probably system time was changed')
        pass

    for record in timeline:
        if record[0] == "Active":
            timeline_colors.append("#2ca02c")
        elif record[0] == "Inactive":
            timeline_colors.append("#eeeeee")
        elif record[0] == "No Data":
            timeline_colors.append("#ffffff")
        elif record[0] == "Camera not found / in use":
            timeline_colors.append("#d62728")

    return timeline, timeline_colors


def get_hourly_data(db_path, date, slot):
    slots = {
        1: ("00:00:00", "01:00:00"),
        2: ("01:00:00", "02:00:00"),
        3: ("02:00:00", "03:00:00"),
        4: ("03:00:00", "04:00:00"),
        5: ("04:00:00", "05:00:00"),
        6: ("05:00:00", "06:00:00"),
        7: ("06:00:00", "07:00:00"),
        8: ("07:00:00", "08:00:00"),
        9: ("08:00:00", "09:00:00"),
        10: ("09:00:00", "10:00:00"),
        11: ("10:00:00", "11:00:00"),
        12: ("11:00:00", "12:00:00"),
        13: ("12:00:00", "13:00:00"),
        14: ("13:00:00", "14:00:00"),
        15: ("14:00:00", "15:00:00"),
        16: ("15:00:00", "16:00:00"),
        17: ("16:00:00", "17:00:00"),
        18: ("17:00:00", "18:00:00"),
        19: ("18:00:00", "19:00:00"),
        20: ("19:00:00", "20:00:00"),
        21: ("20:00:00", "21:00:00"),
        22: ("21:00:00", "22:00:00"),
        23: ("22:00:00", "23:00:00"),
        24: ("23:00:00", "24:00:00")
    }

    try:
        low_time = slots[slot][0]
        high_time = slots[slot][1]
    except KeyError:
        return {}

    global browsers, browsers_real
    browsers = {'Opera': [], 'Chrome': [], 'Microsoft Edge': [], 'Iexplore': [], 'Firefox': [], 'Safari': [],
                'Edge (Chromium)': []}
    browsers_real = {'Opera': [], 'Chrome': [], 'Microsoft Edge': [], 'Iexplore': [], 'Firefox': [], 'Safari': [],
                     'Edge (Chromium)': []}

    colors = [
        '#1f77b4', '#2ca02c', '#d62728', '#ff7f0e', '#9467bd', '#e377c2', '#bcbd22', '#17becf', '#8c564b', '#9edae5',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#7f7f7f'
    ]

    fmt = '%H:%M:%S'
    idle_time = datetime.timedelta(seconds=185)
    today = datetime.date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        'SELECT * FROM tracker WHERE t < time("' + high_time + '") AND t > time("' + low_time + '") AND d = "' + date + '" ')
    data = c.fetchall()

    c.execute('SELECT DISTINCT app FROM tracker WHERE d="' + date + '"')
    applications = c.fetchall()
    # create dictionary
    apps = {}
    apps_colors = {}
    timeline = []
    timeline_colors = []

    for row in applications:
        app_name = row[0].split(' - ')[0]
        apps[app_name] = 0
        apps_colors['Inactive'] = '#eeeeee'
        apps_colors['No Data'] = '#ffffff'
        if app_name not in apps_colors:
            apps_colors[app_name] = colors[0]
            colors.append(colors.pop(0))

    try:
        time_large = data[0][4].split('.')[0]  # get time of 1st record
        time_small = low_time  # midnight
        diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small, fmt)  # big - small
        dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
        delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
        midnight_minutes = delta.total_seconds() / 60  # convert to seconds then to minutes

        if midnight_minutes > 3.1:
            timeline.append(["Inactive", midnight_minutes])
        else:
            timeline.append([data[0][1], midnight_minutes])

    except (ValueError, IndexError):
        pass

    x = 1
    while x < len(data):
        try:
            time_large = data[x][4].split('.')[0]  # get time of 2nd record
            time_small = data[x - 1][4].split('.')[0]  # get time of 1st record
            diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small,
                                                                                            fmt)  # big - small
            dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
            delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
            usage_minutes = delta.total_seconds() / 60  # convert to seconds then to minutes
        except ValueError:
            print('ValueError - Error calculating - Probably system time was changed')
            print("PREVIOUS - " + str(data[x - 1]))
            print("THIS - " + str(data[x]))
            pass

        if diff > idle_time:
            try:
                if timeline[-1][0] == "Inactive":
                    timeline[-1][1] += usage_minutes
                else:
                    timeline.append(["Inactive", usage_minutes])
            except IndexError:
                timeline.append(["Inactive", usage_minutes])

        else:
            try:
                apps[data[x - 1][1]] += usage_minutes
                # apps[data[x - 1][1].split(' - ')[0]] += usage_minutes  ======= this was here
                # if timeline[-1][0] == data[x - 1][1].split(' - ')[0]: ========== this also
                if timeline[-1][0] == data[x - 1][1]:
                    timeline[-1][1] += usage_minutes
                    try:
                        if data[x - 1][1] in browsers:
                            mid = data[x - 1][6].split('-')
                            if len(mid) > 1:
                                window = '-'.join(mid[:-1])
                            else:
                                window = mid[0]

                            if window not in browsers[data[x - 1][1]]:
                                browsers[data[x - 1][1]].append(window)
                                browsers_real[data[x - 1][1]].append(data[x - 1][4] + '  |  ' + window)

                    except Exception as e:
                        print(e)
                else:
                    # timeline.append([data[x - 1][1].split(' - ')[0], usage_minutes])  ========== this tooo
                    timeline.append([data[x - 1][1], usage_minutes])
                    try:
                        if data[x - 1][1] in browsers:
                            mid = data[x - 1][6].split('-')
                            if len(mid) > 1:
                                window = '-'.join(mid[:-1])
                            else:
                                window = mid[0]
                            if window not in browsers[data[x - 1][1]]:
                                browsers[data[x - 1][1]].append(window)
                                browsers_real[data[x - 1][1]].append(data[x - 1][4] + '  |  ' + window)
                    except Exception as e:
                        print(e)
            except ValueError:
                print('ValueError - Error calculating - Probably system time was changed')
                pass
            except IndexError:
                # timeline.append([data[x - 1][1].split(' - ')[0], usage_minutes]) =========== this as well
                timeline.append([data[x - 1][1], usage_minutes])

        x += 1

    try:
        time_large = high_time  # get time of 2nd record
        time_small = data[-1][4].split('.')[0]  # get time of last record
        diff = datetime.datetime.strptime(time_large, fmt) - datetime.datetime.strptime(time_small, fmt)  # big - small
        dt = datetime.datetime.strptime(str(diff), '%H:%M:%S')  # convert to H-M-S
        delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)  # covert to time delta
        no_data_time = delta.total_seconds() / 60  # convert to seconds then to minutes

        if no_data_time > 3:
            if today == data[-1][3]:
                timeline.append(["No Data", no_data_time])
            else:
                timeline.append(["Inactive", no_data_time])

    except (ValueError, IndexError):
        print('ValueError - Error calculating - Probably system time was changed')
        pass

    for record in timeline:
        timeline_colors.append(apps_colors[record[0]])

    return apps, timeline, timeline_colors, apps_colors


def get_hourly_keystrokes(db_path, date, slot):
    app_words = {}
    slots = {
        1: ("00:00:00", "01:00:00"),
        2: ("01:00:00", "02:00:00"),
        3: ("02:00:00", "03:00:00"),
        4: ("03:00:00", "04:00:00"),
        5: ("04:00:00", "05:00:00"),
        6: ("05:00:00", "06:00:00"),
        7: ("06:00:00", "07:00:00"),
        8: ("07:00:00", "08:00:00"),
        9: ("08:00:00", "09:00:00"),
        10: ("09:00:00", "10:00:00"),
        11: ("10:00:00", "11:00:00"),
        12: ("11:00:00", "12:00:00"),
        13: ("12:00:00", "13:00:00"),
        14: ("13:00:00", "14:00:00"),
        15: ("14:00:00", "15:00:00"),
        16: ("15:00:00", "16:00:00"),
        17: ("16:00:00", "17:00:00"),
        18: ("17:00:00", "18:00:00"),
        19: ("18:00:00", "19:00:00"),
        20: ("19:00:00", "20:00:00"),
        21: ("20:00:00", "21:00:00"),
        22: ("21:00:00", "22:00:00"),
        23: ("22:00:00", "23:00:00"),
        24: ("23:00:00", "24:00:00")
    }

    try:
        low_time = slots[slot][0]
        high_time = slots[slot][1]
    except KeyError:
        return {}

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        'SELECT * FROM key_logger_new WHERE t < time("' + high_time + '") AND t > time("' + low_time + '") AND d = "' + date + '" ')
    data = c.fetchall()

    for row in data:
        app = str(row[2])
        word_count = int(row[6])
        content = row[5]
        copy = int(row[7])
        paste = int(row[8])
        id = "_".join(app.split(" "))
        if app in app_words:
            app_words[app] = (id, app_words[app][1] + "\n" + content, app_words[app][2] + word_count, app_words[app][3] + copy, app_words[app][4] + paste )
        else:
            app_words[app] = (id, content, word_count, copy, paste)

    print(app_words)
    return app_words


def get_hourly_urls(db_path, date, slot):
    url = {}
    slots = {
        1: ("00:00:00", "01:00:00"),
        2: ("01:00:00", "02:00:00"),
        3: ("02:00:00", "03:00:00"),
        4: ("03:00:00", "04:00:00"),
        5: ("04:00:00", "05:00:00"),
        6: ("05:00:00", "06:00:00"),
        7: ("06:00:00", "07:00:00"),
        8: ("07:00:00", "08:00:00"),
        9: ("08:00:00", "09:00:00"),
        10: ("09:00:00", "10:00:00"),
        11: ("10:00:00", "11:00:00"),
        12: ("11:00:00", "12:00:00"),
        13: ("12:00:00", "13:00:00"),
        14: ("13:00:00", "14:00:00"),
        15: ("14:00:00", "15:00:00"),
        16: ("15:00:00", "16:00:00"),
        17: ("16:00:00", "17:00:00"),
        18: ("17:00:00", "18:00:00"),
        19: ("18:00:00", "19:00:00"),
        20: ("19:00:00", "20:00:00"),
        21: ("20:00:00", "21:00:00"),
        22: ("21:00:00", "22:00:00"),
        23: ("22:00:00", "23:00:00"),
        24: ("23:00:00", "24:00:00")
    }

    try:
        low_time = slots[slot][0]
        high_time = slots[slot][1]
    except KeyError:
        return {}

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        'SELECT url, t FROM url_data WHERE end_t < time("' + high_time + '") AND start_t > time("' + low_time + '") AND d = "' + date + '" ')
    data = c.fetchall()

    for row in data:
        if row[0] in url:
            url[row[0]] += row[1]
        else:
            url[row[0]] = row[1]

    return url


def give_clipboard_data(db_path, date):
    clipboard = {}
    clipboard_data_list = []
    row_id = 0
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM clipboard_monitor WHERE d="' + date + '" ORDER BY t')
    data = c.fetchall()

    for row in data:
        app = row[4]
        t = row[2]
        content = row[3]
        if app in clipboard:
            clipboard[app] = clipboard[app] + t + " ===================\n" + content + "\n\n"
        else:
            clipboard[app] = t + " ===================\n" + content + "\n\n"

    for record in clipboard:
        clipboard_data_list.append((row_id, record, clipboard[record]))
        row_id += 1

    return clipboard_data_list


def give_keylogger_data(db_path, date):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM key_logger WHERE d="' + date + '"')
    data = c.fetchall()
    return data


def give_network_data(db_path, date):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM network_monitor WHERE d="' + date + '"')
    data = c.fetchall()
    return data