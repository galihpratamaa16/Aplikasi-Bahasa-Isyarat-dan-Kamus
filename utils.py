import os
import urllib.request

import cv2
import numpy as np
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.image import Image, ImageFormat
from mediapipe.tasks.python.vision.hand_landmarker import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarksConnections,
)

MODEL_URL = 'https://storage.googleapis.com/mediapipe-assets/hand_landmarker.task'
MODEL_PATH = os.path.join('models', 'hand_landmarker.task')


def landmarks_to_features(landmarks):
    """Ubah landmark tangan menjadi vektor fitur yang dinormalisasi."""
    if not landmarks:
        return None

    pts = np.array(landmarks, dtype=np.float32)
    x = pts[:, 0]
    y = pts[:, 1]
    z = pts[:, 2]

    cx = np.mean(x)
    cy = np.mean(y)
    x = x - cx
    y = y - cy

    scale = np.max(np.abs(np.concatenate([x, y, z])))
    if scale > 0:
        x = x / scale
        y = y / scale
        z = z / scale

    return np.concatenate([x, y, z]).astype(np.float32)


def download_hand_landmarker_model(model_path=MODEL_PATH, url=MODEL_URL):
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    if os.path.exists(model_path):
        return model_path

    print(f'Mengunduh model MediaPipe ke {model_path} ...')
    urllib.request.urlretrieve(url, model_path)
    print('Model berhasil diunduh.')
    return model_path


def create_hand_landmarker(model_path=None):
    if model_path is None:
        model_path = download_hand_landmarker_model()

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
    )
    return HandLandmarker.create_from_options(options)


def frame_to_image(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image(ImageFormat.SRGB, rgb)


def draw_hand_landmarks(image, landmarks):
    if not landmarks:
        return image

    height, width = image.shape[:2]
    for connection in HandLandmarksConnections.HAND_CONNECTIONS:
        start = landmarks[connection.start]
        end = landmarks[connection.end]
        cv2.line(
            image,
            (int(start.x * width), int(start.y * height)),
            (int(end.x * width), int(end.y * height)),
            (0, 255, 0),
            2,
        )

    for landmark_point in landmarks:
        cv2.circle(
            image,
            (int(landmark_point.x * width), int(landmark_point.y * height)),
            3,
            (0, 0, 255),
            -1,
        )

    return image
