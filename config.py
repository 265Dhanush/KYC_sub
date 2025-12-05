import mediapipe as mp
from deepface import DeepFace
from flask import Blueprint

print("--- Initializing MediaPipe ---")
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

print("--- Building DeepFace model (this may take a moment)... ---")
try:
    DeepFace.build_model("VGG-Face")
    print("--- Models ready. ---")
except Exception as e:
    print(f"--- FATAL ERROR: Could not build DeepFace model: {e} ---")
    exit()

# Create the Blueprint
# We tell it to look for templates in its 'templates' sub-folder
verification_bp = Blueprint(
    'live_verification',
    __name__,
    template_folder='templates'
)

# Import the routes file (at the bottom) to avoid circular imports
import routes