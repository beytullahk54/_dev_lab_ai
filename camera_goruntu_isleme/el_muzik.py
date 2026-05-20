import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import pygame
import os
import sys
import time
import urllib.request
import ssl
import certifi

pygame.mixer.init()

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

_frame_timestamp_ms = 0

MUSIC_FILE = "muzik.mp3"
music_playing = False
hand_was_up = False
cooldown_until = 0

def find_music_file():
    if os.path.exists(MUSIC_FILE):
        return MUSIC_FILE
    for ext in ['.mp3', '.wav', '.ogg']:
        for f in os.listdir('.'):
            if f.lower().endswith(ext):
                return f
    return None

def play_music(file_path):
    global music_playing
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(-1)
        music_playing = True
        print("▶ Müzik çalıyor...")
    except Exception as e:
        print(f"Müzik çalma hatası: {e}")

def stop_music():
    global music_playing
    pygame.mixer.music.stop()
    music_playing = False
    print("⏹ Müzik durduruldu")

WRIST = 0
MIDDLE_FINGER_TIP = 12
INDEX_FINGER_TIP = 8

def is_hand_up(landmarks):
    wrist_y = landmarks[WRIST].y
    middle_tip_y = landmarks[MIDDLE_FINGER_TIP].y
    index_tip_y = landmarks[INDEX_FINGER_TIP].y
    
    return middle_tip_y < wrist_y and index_tip_y < wrist_y

def main():
    global hand_was_up, cooldown_until
    
    music_file = find_music_file()
    if not music_file:
        print("⚠️ Müzik dosyası bulunamadı!")
        print("Lütfen 'muzik.mp3' veya benzeri bir ses dosyası ekleyin.")
        print("Uygulama el izleme modunda çalışacak.")
    else:
        print(f"🎵 Müzik dosyası: {music_file}")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Kamera açılamadı!")
        sys.exit(1)
    
    print("\n🖐 El kaldırdığınızda müzik çalacak, indirdiğinizde duracak")
    print("⛔ Çıkmak için 'q' tuşuna basın\n")
    
    global _frame_timestamp_ms

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        _frame_timestamp_ms += 33
        results = hhands.detect_for_video(mp_image, _frame_timestamp_ms)
        
        hand_up = False
        status_text = "El Algılanmadı"
        status_color = (128, 128, 128)
        
        if results.hand_landmarks:
            for hand_landmarks_list in results.hand_landmarks:
                h, w = frame.shape[:2]
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks_list]
                for a, b in HAND_CONNECTIONS:
                    cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
                for pt in pts:
                    cv2.circle(frame, pt, 4, (0, 0, 255), -1)
                
                if is_hand_up(hand_landmarks_list):
                    hand_up = True
                    status_text = "✋ EL KALDIRILDI - Müzik Çalıyor"
                    status_color = (0, 255, 0)
                else:
                    status_text = "✊ El İndirildi - Müzik Durdu"
                    status_color = (0, 0, 255)
        
        current_time = time.time()
        
        if music_file:
            if hand_up and not hand_was_up and current_time > cooldown_until:
                if not music_playing:
                    play_music(music_file)
                cooldown_until = current_time + 0.5
            elif not hand_up and hand_was_up:
                if music_playing:
                    stop_music()
        
        hand_was_up = hand_up
        
        cv2.rectangle(frame, (0, 0), (400, 50), (0, 0, 0), -1)
        cv2.putText(frame, status_text, (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        if music_file:
            music_status = "🎵 Çalıyor" if music_playing else "🔇 Sessiz"
            cv2.putText(frame, music_status, (frame.shape[1] - 150, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('El Muzik Kontrolu', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()
    print("\n👋 Görüşmek üzere!")

if __name__ == "__main__":
    main()
