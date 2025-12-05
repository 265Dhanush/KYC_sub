import cv2
import numpy as np
from scipy.spatial import distance as dist
from deepface import DeepFace

# --- Constants ---
EAR_THRESHOLD = 0.20
EAR_CONSEC_FRAMES = 2
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_INDICES = [362, 387, 385, 263, 380, 373]

# --- Global variable for status ---
verification_status = ["Pending"]
FRAME_COUNTER = 0

def calculate_ear(eye_points):
    """Helper function to calculate the Eye Aspect Ratio"""
    A = dist.euclidean(eye_points[1], eye_points[5])
    B = dist.euclidean(eye_points[2], eye_points[4])
    C = dist.euclidean(eye_points[0], eye_points[3])
    ear = (A + B) / (2.0 * C)
    return ear

def generate_frames(reference_image_path, face_mesh_model):
    #Generator function for streaming video frames with liveness & verification.
    global FRAME_COUNTER, verification_status
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("--- FATAL ERROR: Cannot open webcam. ---")
        return

    print("--- Webcam opened. Streaming started. ---")

    try:
        while True:
            success, image = cap.read()
            if not success:
                break

            original_image = image.copy()
            image = cv2.flip(image, 1)
            image_height, image_width, _ = image.shape

            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh_model.process(image_rgb)
            image.flags.writeable = True

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                
                left_eye_points = []
                for idx in LEFT_EYE_INDICES:
                    x = int(landmarks[idx].x * image_width)
                    y = int(landmarks[idx].y * image_height)
                    left_eye_points.append((x, y))

                right_eye_points = []
                for idx in RIGHT_EYE_INDICES:
                    x = int(landmarks[idx].x * image_width)
                    y = int(landmarks[idx].y * image_height)
                    right_eye_points.append((x, y))

                left_ear = calculate_ear(left_eye_points)
                right_ear = calculate_ear(right_eye_points)
                ear = (left_ear + right_ear) / 2.0

                if ear < EAR_THRESHOLD:
                    FRAME_COUNTER += 1
                else:
                    if FRAME_COUNTER >= EAR_CONSEC_FRAMES:
                        print("BLINK DETECTED! Running verification...")
                        
                        try:
                            result = DeepFace.verify(
                                img1_path=reference_image_path, 
                                img2_path=original_image,
                                model_name="VGG-Face",
                                enforce_detection=False
                            )
                            
                            if result["verified"]:
                                verification_status[0] = "VERIFIED"
                            else:
                                verification_status[0] = "UNVERIFIED"
                            
                            print(f"Status: {verification_status[0]}, Distance: {result['distance']:.4f}")

                        except Exception as e:
                            print(f"Verification error: {e}")
                            verification_status[0] = "Error"
                    
                    FRAME_COUNTER = 0

            status = verification_status[0]
            status_color = (0, 255, 0) if status == "VERIFIED" else (0, 0, 255)
            cv2.putText(image, f"Status: {status}", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.putText(image, "Blink to verify.", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            (flag, buffer) = cv2.imencode('.jpg', image)
            if not flag:
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytearray(buffer) + b'\r\n')
    finally:
        print("--- Releasing webcam ---")
        cap.release()