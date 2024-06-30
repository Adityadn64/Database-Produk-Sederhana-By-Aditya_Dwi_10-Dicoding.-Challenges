try:
    import os
    import requests
    
    if os.system('python3 -m pip install -U cmake dlib'):
    
        import dlib
        
        # URL untuk mendownload model-weight
        url = {
            "Auth/Model/Weight/shape_predictor_68_face_landmarks.dat": "https://github.com/italojs/facial-landmarks-recognition/raw/master/shape_predictor_68_face_landmarks.dat",
            "Auth/Model/Weight/dlib_face_recognition_resnet_model_v1.dat": "https://github.com/ageitgey/face_recognition_models/raw/master/face_recognition_models/models/dlib_face_recognition_resnet_model_v1.dat"
        }
        
        # Loop untuk download file dari URL
        for key, value in url.items():
            if not os.path.exists(key):
                os.makedirs(os.path.dirname(key), exist_ok=True)
                
                print(f"Downloading {value} ...")
        
                try:
                    # Download file dari URL
                    response = requests.get(value)
                    response.raise_for_status()  # Menangani kesalahan jika download gagal
        
                    # Simpan file yang didownload
                    with open(key, "wb") as file:
                        file.write(response.content)
        
                    print(f"Download of {key} completed.")
        
                except requests.exceptions.RequestException as e:
                    print(f"Error during download: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")
        
        # Setelah selesai download, inisialisasi detektor wajah, prediktor, dan model pengenalan wajah
        if all(os.path.exists(path) for path in url.keys()):
            # Inisialisasi detektor wajah
            detector = dlib.get_frontal_face_detector()
            # Inisialisasi prediktor bentuk
            predictor_path = "Auth/Model/Weight/shape_predictor_68_face_landmarks.dat"
            predictor = dlib.shape_predictor(predictor_path)
            # Inisialisasi pengenalan wajah
            face_rec_path = "Auth/Model/Weight/dlib_face_recognition_resnet_model_v1.dat"
            face_rec = dlib.face_recognition_model_v1(face_rec_path)
        
            face_model = 'Auth/Model/Saved'
            my_face = os.path.join(os.getcwd(), face_model, os.listdir(face_model)[0])
            print("Ok")
        else:
            print("Failed to download one or more required files. Exiting...")
            
except Exception as e: print(e)
    
