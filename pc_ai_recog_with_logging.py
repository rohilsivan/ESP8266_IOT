#!/usr/bin/env python3
# File: pc_ai_recog_with_logging.py

import cv2
import face_recognition
import numpy as np
import os
import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import queue
import requests
import argparse
import csv
import tempfile
import shutil
import sys

# =========================
# CAMERA CONFIGURATION
# =========================
camera_source = 0

# =========================
# MQTT / TOPICS
# =========================
BROKER = "192.168.137.1"
TOPIC_AI = "factory/alert"
TOPIC_PANIC = "esp/panic"
TOPIC_PRESENCE = "esp/presence"

# =========================
# LOG FILE
# =========================
LOG_CSV = os.path.join(tempfile.gettempdir(), "events_log.csv")
print("[DEBUG] Logging to:", LOG_CSV)

if not os.path.exists(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ts", "event_type", "details"])


def log_event(event_type, details):
    ts = datetime.now().isoformat(timespec="seconds")
    with open(LOG_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([ts, event_type, details])
    print(f"[LOG] {ts} | {event_type} | {details}")


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


# =========================
# LOAD KNOWN FACES
# =========================
def load_known_faces(folder="faces"):
    encodings, names = [], []
    for file in os.listdir(folder):
        if file.lower().endswith(('.jpg', '.png', '.jpeg')):
            path = os.path.join(folder, file)
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            if len(encs) > 0:
                encodings.append(encs[0])
                names.append(os.path.splitext(file)[0])
                print(f"[INFO] Loaded authorized face: {file}")
    return encodings, names


# =========================
# CAMERA FRAME SOURCE
# =========================
frame_queue = queue.Queue(maxsize=1)


def get_ip_frame(ip_url):
    try:
        resp = requests.get(ip_url, stream=True, timeout=1)
        img_arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def start_camera(camera_source):
    if isinstance(camera_source, int):
        cap = cv2.VideoCapture(camera_source)
        return cap, None
    else:
        def fetch_frames():
            while True:
                f = get_ip_frame(camera_source)
                if f is not None:
                    if frame_queue.full():
                        frame_queue.get_nowait()
                    frame_queue.put(f)
                else:
                    time.sleep(0.05)
        threading.Thread(target=fetch_frames, daemon=True).start()
        return None, frame_queue


# =========================
# COPY LOG FILE TO PROJECT FOLDER
# =========================
def background_log_copy():
    dst = os.path.join(os.getcwd(), "latest_log.csv")
    while True:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                shutil.copyfile(LOG_CSV, tmp.name)
                shutil.move(tmp.name, dst)
        except PermissionError:
            pass
        except Exception as e:
            print(f"[WARN] Background copy error: {e}", file=sys.stderr)
        time.sleep(2)


# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", default=BROKER)
    parser.add_argument("--camera", default=None)
    args = parser.parse_args()

    broker = args.broker
    client = mqtt.Client(client_id="PC_AI_Recog_logger")
    client.connect(broker, 1883, 60)
    client.loop_start()

    presence_flag = {"present": False}

    # ===========================================
    # WE REMOVE presence logging completely
    # ONLY toggle camera on/off
    # ===========================================
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode(errors="ignore")
        print(f"[MQTT IN] {topic}: {payload}")

        if topic == TOPIC_PANIC:
            log_event("panic", payload)

        elif topic == TOPIC_PRESENCE:
            if "enter" in payload:
                presence_flag["present"] = True
            elif "leave" in payload:
                presence_flag["present"] = False

    client.subscribe(TOPIC_PANIC)
    client.subscribe(TOPIC_PRESENCE)
    client.on_message = on_message

    known_encodings, known_names = load_known_faces("faces")
    if not known_encodings:
        print("[ERROR] No authorized faces found!")
        return

    global camera_source
    if args.camera is not None:
        try:
            camera_source = int(args.camera)
        except:
            camera_source = args.camera

    cap, q = start_camera(camera_source)
    print("[INFO] Face Recognition + Logger Started")

    threading.Thread(target=background_log_copy, daemon=True).start()

    last_state = None
    last_pub = 0

    try:
        while True:

            # ===========================
            # WAIT FOR PRESENCE SENSOR
            # ===========================
            if not presence_flag["present"]:
                idle = np.zeros((240, 480, 3), dtype=np.uint8)
                cv2.putText(idle, "Idle - waiting for presence", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow("AI Face Recognition Monitor", idle)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                continue

            # ===========================
            # READ FRAME
            # ===========================
            if cap:
                ret, frame = cap.read()
                if not ret:
                    continue
            else:
                if q.empty():
                    continue
                frame = q.get()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, faces)

            current_state = "no_face"
            label_text = "No Face"
            color = (0, 0, 255)

            for encoding, (top, right, bottom, left) in zip(encodings, faces):
                matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.45)
                face_distances = face_recognition.face_distance(known_encodings, encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    label_text = f"Authorized: {name}"
                    color = (0, 255, 0)
                    current_state = "authorized"
                else:
                    label_text = "Unauthorized!"
                    color = (0, 0, 255)
                    current_state = "unauthorized"

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label_text, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # ==========================================================
            # FINAL FILTER → ONLY authorized events are saved + shown
            # ==========================================================
            if current_state != last_state and (time.time() - last_pub) > 1:

                # skip no_face + unauthorized
                if current_state != "authorized":
                    last_state = current_state
                    last_pub = time.time()
                    continue

                msg = {
                    "type": "AI_AUTH_OK",
                    "state": current_state,
                    "reason": label_text,
                    "ts": now_iso()
                }

                client.publish(TOPIC_AI, json.dumps(msg))
                print(f"[MQTT] Published: {msg}")
                log_event("ai_event", json.dumps(msg))

                last_state = current_state
                last_pub = time.time()

            cv2.imshow("AI Face Recognition Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass

    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        client.loop_stop()
        client.disconnect()

        dst = os.path.join(os.getcwd(), "latest_log.csv")
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                shutil.copyfile(LOG_CSV, tmp.name)
                shutil.move(tmp.name, dst)
            print("[INFO] Final log copy complete.")
        except:
            print("[WARN] Could not copy final log file.")


if __name__ == "__main__":
    main()
