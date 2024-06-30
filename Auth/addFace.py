import cv2, os, numpy as np, dlib

os.system('cls')

# Inisialisasi detektor wajah
detector = dlib.get_frontal_face_detector()
# Inisialisasi prediktor bentuk
predictor = dlib.shape_predictor(os.path.join(os.getcwd(), 'Auth/Model/Weight/shape_predictor_68_face_landmarks.dat'))
# Inisialisasi pengenalan wajah
face_rec = dlib.face_recognition_model_v1(os.path.join(os.getcwd(), 'Auth/Model/Weight/dlib_face_recognition_resnet_model_v1.dat'))

face_model = 'Auth/Model/Saved'
my_face = os.path.join(os.getcwd(), face_model, os.listdir(face_model)[0])

# Buka kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Tidak dapat membaca frame dari kamera")
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

        # Simpan deskripsi wajah ke file
        np.save(my_face, face_descriptor)
        print("Deskripsi wajah disimpan.")

        # Tampilkan hasil deteksi
        (x, y, w, h) = (face.left(), face.top(), face.width(), face.height())
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Face', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
