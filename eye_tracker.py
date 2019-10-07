import cv2
import time
import threading
import sqlite3
import datetime

FACE = 0


def main(db_path):
    global FACE
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    vs = cv2.VideoCapture(0)

    face_detected = 0
    eyes_detected = 0
    no_video = 0

    t_end = time.time() + 5
    while time.time() < t_end:

        ret, frame = vs.read()

        if frame is None:
            print("Cant capture video")
            no_video = 1
            break

        faces = faceCascade.detectMultiScale(frame)

        if faces != ():
            print("Face Detected")
            face_detected = 1
            FACE = 1
        else:
            # print("No face")
            FACE = 0
            pass

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            crop_img = frame[y:y + h, x:x + w]
            eyes = eyeCascade.detectMultiScale(crop_img, 1.3, 5)

            if eyes != ():
                eyes_detected = 1
                push_data(db_path, no_video, face_detected, eyes_detected)
                cv2.destroyAllWindows()
                return
            else:
                print("No eyes")
                pass

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    push_data(db_path, no_video, face_detected, eyes_detected)
    return


def push_data(db_path, no_video, face_detected, eyes_detected):
    d = datetime.datetime.now()
    date_d = str(d).split(" ")[0]
    time_t = (str(d).split(" ")[1]).split('.')[0]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = "INSERT INTO eye_tracker(d, t, no_video, face, eyes) VALUES('" + date_d + "','" + time_t + "','" + str(no_video) + "','" + str(face_detected) + "','" + str(eyes_detected) + "')"
    c.execute(query)
    conn.commit()
    return


def timed_runs(kill_flag, db_path):
    time_loop = 180
    while not kill_flag.isSet():
        if time_loop % 180 == 0:
            time_loop = 5
            threading.Thread(target=main, args=(db_path,)).start()
        else:
            time_loop += 5
        time.sleep(5)





