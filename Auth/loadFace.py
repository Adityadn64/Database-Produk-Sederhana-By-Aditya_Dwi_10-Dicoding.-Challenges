import cv2
import numpy as np
from weight import *

# Muat deskripsi wajah yang dikenal
known_face_descriptor = np.load(my_face)

# Buka kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Deteksi wajah
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        # Prediksi landmark wajah
        shape = predictor(gray, face)
        # Dapatkan deskripsi wajah
        face_descriptor = face_rec.compute_face_descriptor(frame, shape)
        face_descriptor = np.array(face_descriptor)

        # Hitung jarak antara wajah yang dikenali dengan wajah saat ini
        distance = np.linalg.norm(known_face_descriptor - face_descriptor)

        if distance < 0.5:  # Threshold untuk verifikasi wajah
            print("Wajah dikenali, akses diberikan!")
            text = "Access Granted"
            # Implementasikan logika masuk ke web di sini
        else:
            print("Wajah tidak dikenali, akses ditolak.")
            text = "Access Denied"

        # Tampilkan hasil deteksi
        (x, y, w, h) = (face.left(), face.top(), face.width(), face.height())
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow('Face', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
