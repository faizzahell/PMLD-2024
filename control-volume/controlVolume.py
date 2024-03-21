import cv2
import mediapipe as mp
import osascript

# Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Inisialisasi OpenCV
cap = cv2.VideoCapture(0)

# Inisialisasi volume
current_volume = 50  # Volume awal
volume_increment = 2  # Nilai penambahan atau pengurangan volume

# Lebar dan tinggi indikator volume
indicator_width = 300
indicator_height = 20

while cap.isOpened():
    ret, frame = cap.read()

    # Konversi frame menjadi RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Deteksi tangan menggunakan MediaPipe
    results = hands.process(rgb_frame)

    # Di dalam loop while
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Hitung jarak antara ibu jari dan jari telunjuk
            distance = abs(thumb_tip.x - index_tip.x)

            # Mengontrol volume berdasarkan jarak antara ibu jari dan jari telunjuk
            if distance < 0.05:
                # Tingkatkan volume
                current_volume = max(0, current_volume - volume_increment)
                osascript.run(f"set volume output volume {current_volume}")
                indicator_text = f"Volume Down: {current_volume}"
                
            elif distance > 0.2:
                # Kurangi volume                
                current_volume = min(100, current_volume + volume_increment)
                osascript.run(f"set volume output volume {current_volume}")
                indicator_text = f"Volume Up: {current_volume}"
            else:
                indicator_text = "Volume Stable"

            # Gambar garis tangan
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Tambahkan indikator volume dalam bentuk bar horizontal
            indicator_position = (10, 15)  # Posisi indikator pada layar
            cv2.rectangle(frame, (indicator_position[0], indicator_position[1]),
                          (indicator_position[0] + indicator_width, indicator_position[1] + indicator_height),
                          (0, 0, 0), -1)  # Gambar kotak hitam sebagai latar belakang indikator
            cv2.rectangle(frame, (indicator_position[0], indicator_position[1]),
                          (indicator_position[0] + int(indicator_width * (current_volume / 100)), 
                           indicator_position[1] + indicator_height),
                          (0, 255, 0), -1)  # Gambar bar hijau sebagai indikator volume

            # Tambahkan indikator volume pada tampilan kamera
            cv2.putText(frame, indicator_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Tambahkan garis yang menunjukkan jarak antara ibu jari dan jari telunjuk
            thumb_tip_x, thumb_tip_y = int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0])
            index_tip_x, index_tip_y = int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])
            cv2.line(frame, (thumb_tip_x, thumb_tip_y), (index_tip_x, index_tip_y), (255, 0, 0), 2)

            # Tambahkan bentuk bulat di ujung garis sebagai indikator
            cv2.circle(frame, (thumb_tip_x, thumb_tip_y), 5, (0, 0, 255), -1)  # Warna merah di ujung ibu jari
            cv2.circle(frame, (index_tip_x, index_tip_y), 5, (0, 0, 255), -1)  # Warna merah di ujung jari telunjuk

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
