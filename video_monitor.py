import threading
import time
import compare_audio
import compare_screenshots
import eye_tracker
import datetime
import sqlite3

has_youtube = 0


def set_youtube(yt):
    global has_youtube
    print(yt)
    has_youtube = yt


def timed_runs(kill_flag, db_path):
    threading.Thread(name="eye tracker thread", target=eye_tracker.timed_runs, args=(kill_flag, db_path)).start()
    global face_detected, has_youtube
    time_loop = 180

    while not kill_flag.isSet():
        if time_loop % 180 == 0:
            time_loop = 5
            audio_playing = compare_audio.main()
            video_playing = compare_screenshots.main()
            face_detected = eye_tracker.FACE

            print("audio - " + str(audio_playing) + " | video - " + str(video_playing) + " | face - " + str(face_detected))

            if audio_playing and video_playing and face_detected:
                d = datetime.datetime.now()
                date_d = str(d).split(" ")[0]
                time_t = (str(d).split(" ")[1]).split(".")[0]
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                query = "INSERT INTO video_monitor(d, t) VALUES('" + date_d + "','" + time_t + "')"
                c.execute(query)
                conn.commit()
        else:
            time_loop += 5
        time.sleep(5)

