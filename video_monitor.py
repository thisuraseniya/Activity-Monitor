import threading
import compare_audio
import compare_screenshots
import eye_tracker
import datetime
import sqlite3

has_youtube = 0


def set_youtube(yt):
    global has_youtube
    # print("Has youtube", yt)
    has_youtube = yt


def run_eye_tracker(kill_flag, db_path):
    threading.Thread(name="eye tracker thread", target=eye_tracker.timed_runs, args=(kill_flag, db_path,)).start()


def run_video_monitor(db_path):
    global face_detected, has_youtube

    if has_youtube:
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

    return
