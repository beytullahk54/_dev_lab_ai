import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import os
import time
import threading
import urllib.request
import ssl
import certifi
import subprocess
from flask import Flask, Response, jsonify, send_from_directory, request

app = Flask(__name__, static_folder="static")

MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
os.makedirs(MUSIC_DIR, exist_ok=True)


def load_settings():
    try:
        with open(SETTINGS_FILE) as f:
            import json
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    import json
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Model indiriliyor...")
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(MODEL_URL, context=ssl_ctx) as response, \
         open(MODEL_PATH, "wb") as f:
        f.write(response.read())
    print("Model indirildi.")

_base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
_options = mp_vision.HandLandmarkerOptions(
    base_options=_base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    running_mode=mp_vision.RunningMode.VIDEO
)
hhands = mp_vision.HandLandmarker.create_from_options(_options)

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17)
]

WRIST = 0
MIDDLE_FINGER_TIP = 12
INDEX_FINGER_TIP = 8
THUMB_TIP = 4

WIGGLE_THRESHOLD = 0.04
WIGGLE_COOLDOWN = 0.8
_prev_index_y = None
_prev_middle_y = None
_index_wiggle_cooldown = 0.0
_middle_wiggle_cooldown = 0.0
_index_last_dir = None
_middle_last_dir = None

state = {
    "hand_up": False,
    "status": "El Algılanmadı",
    "music_playing": False,
    "hand_was_up": False,
    "cooldown_until": 0,
    "frame_ts": 0,
    "music_file": None,
    "music_duration": 0.0,
    "camera_on": False,
    "seek_event": None,
    "resume_pos": 0.0,
    "restart_mode": load_settings().get("restart_mode", False),
}

_music_lock = threading.Lock()
_music_proc = None
_music_pos = 0.0
_music_start_time = 0.0


def _play_music(file_path, start_pos=0.0):
    global _music_proc, _music_pos, _music_start_time
    with _music_lock:
        if _music_proc and _music_proc.poll() is None:
            _music_proc.terminate()
            try:
                _music_proc.wait(timeout=1)
            except Exception:
                _music_proc.kill()
        _music_proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-ss", str(max(0.0, start_pos)), file_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        _music_start_time = time.time() - start_pos
        _music_pos = start_pos


def _stop_music_proc():
    global _music_proc
    with _music_lock:
        if _music_proc and _music_proc.poll() is None:
            _music_proc.terminate()
            try:
                _music_proc.wait(timeout=1)
            except Exception:
                _music_proc.kill()
        _music_proc = None


def _seek_music(file_path, delta_sec):
    global _music_proc, _music_pos, _music_start_time
    with _music_lock:
        elapsed = time.time() - _music_start_time
        new_pos = max(0.0, elapsed + delta_sec)
        if _music_proc and _music_proc.poll() is None:
            _music_proc.terminate()
            try:
                _music_proc.wait(timeout=1)
            except Exception:
                _music_proc.kill()
        _music_proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-ss", str(new_pos), file_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        _music_start_time = time.time() - new_pos
        _music_pos = new_pos

lock = threading.Lock()
cap = None


def list_music_files():
    files = []
    for f in sorted(os.listdir(MUSIC_DIR)):
        if f.lower().endswith((".mp3", ".wav", ".ogg")):
            files.append(f)
    return files


def find_music_file():
    settings = load_settings()
    saved = settings.get("music_file")
    if saved:
        full = os.path.join(MUSIC_DIR, saved)
        if os.path.exists(full):
            return full
    files = list_music_files()
    if files:
        return os.path.join(MUSIC_DIR, files[0])
    return None


def get_music_duration(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            capture_output=True, text=True, timeout=5
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


RING_FINGER_TIP = 16
PINKY_TIP = 20
INDEX_MCP = 5
MIDDLE_MCP = 9


def is_hand_up(landmarks):
    return (landmarks[MIDDLE_FINGER_TIP].y < landmarks[WRIST].y and
            landmarks[INDEX_FINGER_TIP].y < landmarks[WRIST].y)


def is_fist(landmarks):
    tips = [INDEX_FINGER_TIP, MIDDLE_FINGER_TIP, RING_FINGER_TIP, PINKY_TIP]
    mcps = [INDEX_MCP, MIDDLE_MCP, 13, 17]
    return all(landmarks[tip].y > landmarks[mcp].y for tip, mcp in zip(tips, mcps))


def _check_wiggle(prev_y, curr_y, last_dir, cooldown_until, current_time):
    if prev_y is None:
        return False, last_dir
    delta = curr_y - prev_y
    if abs(delta) < WIGGLE_THRESHOLD:
        return False, last_dir
    new_dir = "down" if delta > 0 else "up"
    triggered = False
    if new_dir != last_dir and last_dir is not None and current_time > cooldown_until:
        triggered = True
    return triggered, new_dir


def generate_frames():
    global cap, _prev_index_y, _prev_middle_y
    global _index_wiggle_cooldown, _middle_wiggle_cooldown
    global _index_last_dir, _middle_last_dir
    while True:
        with lock:
            if not state["camera_on"] or cap is None or not cap.isOpened():
                time.sleep(0.05)
                continue
            local_cap = cap

        ret, frame = local_cap.read()

        if not ret or frame is None:
            time.sleep(0.05)
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        with lock:
            state["frame_ts"] += 33
            ts = state["frame_ts"]

        results = hhands.detect_for_video(mp_image, ts)

        hand_up = False
        fist = False
        status = "El Algılanmadı"
        seek_action = None
        current_time = time.time()

        if results.hand_landmarks:
            for lm_list in results.hand_landmarks:
                h, w = frame.shape[:2]
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in lm_list]
                for a, b in HAND_CONNECTIONS:
                    cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
                for pt in pts:
                    cv2.circle(frame, pt, 5, (0, 0, 255), -1)
                if is_fist(lm_list):
                    fist = True
                    status = "Yumruk - Dur"
                elif is_hand_up(lm_list):
                    hand_up = True
                    status = "El Kaldırıldı"
                else:
                    status = "El İndirildi"

                idx_y = lm_list[INDEX_FINGER_TIP].y - lm_list[INDEX_MCP].y
                mid_y = lm_list[MIDDLE_FINGER_TIP].y - lm_list[MIDDLE_MCP].y

                idx_trig, _index_last_dir = _check_wiggle(
                    _prev_index_y, idx_y, _index_last_dir,
                    _index_wiggle_cooldown, current_time)
                mid_trig, _middle_last_dir = _check_wiggle(
                    _prev_middle_y, mid_y, _middle_last_dir,
                    _middle_wiggle_cooldown, current_time)

                if idx_trig:
                    seek_action = 30
                    _index_wiggle_cooldown = current_time + WIGGLE_COOLDOWN
                elif mid_trig:
                    seek_action = -30
                    _middle_wiggle_cooldown = current_time + WIGGLE_COOLDOWN

                _prev_index_y = idx_y
                _prev_middle_y = mid_y


        do_play = None
        do_stop = False
        do_seek = None
        with lock:
            mf = state["music_file"]
            was_up = state["hand_was_up"]
            cooldown = state["cooldown_until"]
            music_playing = state["music_playing"]

            if mf:
                if hand_up and not music_playing and current_time > cooldown:
                    state["music_playing"] = True
                    do_play = 0.0 if state["restart_mode"] else state["resume_pos"]
                    state["cooldown_until"] = current_time + 1.0
                elif fist and music_playing:
                    elapsed = time.time() - _music_start_time
                    state["resume_pos"] = max(0.0, elapsed)
                    state["music_playing"] = False
                    do_stop = True

                if seek_action is not None and music_playing:
                    do_seek = seek_action

            state["hand_was_up"] = hand_up
            state["hand_up"] = hand_up
            state["status"] = status
            mp_str = state["music_playing"]

        if do_play is not None and mf:
            threading.Thread(target=_play_music, args=(mf, do_play), daemon=True).start()
        elif do_stop:
            threading.Thread(target=_stop_music_proc, daemon=True).start()
        elif do_seek is not None and mf:
            threading.Thread(target=_seek_music, args=(mf, do_seek), daemon=True).start()

        color = (0, 0, 220) if fist else ((0, 200, 0) if hand_up else (180, 180, 180))
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (0, 0, 0), -1)
        cv2.putText(frame, status, (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        if mp_str:
            pos_sec = int(time.time() - _music_start_time)
            pos_str = f"{pos_sec // 60}:{pos_sec % 60:02d}"
            music_label = f"harikasin: {pos_str}"
        else:
            music_label = "Muzik: Sessiz"
        cv2.putText(frame, music_label, (frame.shape[1] - 220, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        if do_seek == 30:
            cv2.putText(frame, ">> +30sn", (frame.shape[1]//2 - 80, frame.shape[0]//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
        elif do_seek == -30:
            cv2.putText(frame, "<< -30sn", (frame.shape[1]//2 - 80, frame.shape[0]//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 200, 255), 3)

        guide = [
            "El Kontrolleri:",
            " Ell Kaldir  -> Calar",
            " Yumruk      -> Durur",
            " 1.Parmak ^v -> +30sn",
            " 2.Parmak ^v -> -30sn",
        ]
        gh = frame.shape[0]
        y0 = gh - len(guide) * 22 - 10
        cv2.rectangle(frame, (0, y0 - 5), (260, gh), (0, 0, 0), -1)
        for i, line in enumerate(guide):
            cv2.putText(frame, line, (8, y0 + i * 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/status")
def status():
    with lock:
        pos = round(time.time() - _music_start_time, 1) if state["music_playing"] else round(state["resume_pos"], 1)
        return jsonify({
            "hand_up": state["hand_up"],
            "status": state["status"],
            "music_playing": state["music_playing"],
            "camera_on": state["camera_on"],
            "music_file": state["music_file"],
            "music_pos": pos,
            "music_duration": state["music_duration"],
            "restart_mode": state["restart_mode"],
        })


@app.route("/music/upload", methods=["POST"])
def music_upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False, "error": "Dosya yok"}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in [".mp3", ".wav", ".ogg"]:
        return jsonify({"ok": False, "error": "Desteklenmeyen format"}), 400
    save_path = os.path.join(MUSIC_DIR, f.filename)
    f.save(save_path)
    dur = get_music_duration(save_path)
    _s = load_settings(); _s["music_file"] = f.filename; save_settings(_s)
    with lock:
        state["music_file"] = save_path
        state["music_duration"] = dur
        state["resume_pos"] = 0.0
    return jsonify({"ok": True, "filename": f.filename, "duration": dur})


@app.route("/music/list")
def music_list():
    return jsonify({"files": list_music_files()})


@app.route("/music/select", methods=["POST"])
def music_select():
    import json as _json
    data = request.get_json()
    filename = data.get("filename", "") if data else ""
    full = os.path.join(MUSIC_DIR, filename)
    if not os.path.exists(full):
        return jsonify({"ok": False, "error": "Dosya bulunamadı"}), 404
    dur = get_music_duration(full)
    _s = load_settings(); _s["music_file"] = filename; save_settings(_s)
    with lock:
        state["music_file"] = full
        state["music_duration"] = dur
        state["resume_pos"] = 0.0
    return jsonify({"ok": True, "filename": filename, "duration": dur})


@app.route("/music/restart_mode", methods=["POST"])
def toggle_restart_mode():
    with lock:
        state["restart_mode"] = not state["restart_mode"]
        new_mode = state["restart_mode"]
    settings = load_settings()
    settings["restart_mode"] = new_mode
    save_settings(settings)
    return jsonify({"restart_mode": new_mode})


@app.route("/camera/on", methods=["POST"])
def camera_on():
    global cap
    with lock:
        if state["camera_on"]:
            return jsonify({"ok": True})
        new_cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
        if not new_cap.isOpened():
            new_cap = cv2.VideoCapture(0)
        if not new_cap.isOpened():
            return jsonify({"ok": False, "error": "Kamera açılamadı"}), 500

    for _ in range(10):
        new_cap.read()

    with lock:
        cap = new_cap
        state["camera_on"] = True
        mf = find_music_file()
        state["music_file"] = mf
        state["music_duration"] = get_music_duration(mf) if mf else 0.0
    return jsonify({"ok": True})


@app.route("/camera/off", methods=["POST"])
def camera_off():
    global cap
    old_cap = None
    with lock:
        state["camera_on"] = False
        state["music_playing"] = False
        state["hand_up"] = False
        state["status"] = "El Algılanmadı"
        if cap:
            old_cap = cap
            cap = None
    if old_cap:
        old_cap.release()
    _stop_music_proc()
    return jsonify({"ok": True})


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("Tarayıcıda açın: http://127.0.0.1:5001")
    app.run(host="0.0.0.0", port=5001, threaded=True)
