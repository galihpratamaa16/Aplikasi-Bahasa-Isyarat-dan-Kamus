import base64
import os
import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request
from joblib import load
from utils import (
    create_hand_landmarker,
    download_hand_landmarker_model,
    frame_to_image,
    landmarks_to_features,
)

MODEL_PATH = 'model.pkl'
SIGN_LETTERS = [chr(code) for code in range(65, 91)]

app = Flask(__name__)


def load_model():
    if not os.path.exists(MODEL_PATH):
        return None

    try:
        return load(MODEL_PATH)
    except Exception:
        return None


def prepare_detector():
    if not os.path.exists(os.path.join('models', 'hand_landmarker.task')):
        download_hand_landmarker_model()
    return create_hand_landmarker()


def build_sign_list():
    signs = []
    for letter in SIGN_LETTERS:
        image_name = f'Huruf {letter}.png'
        signs.append({'name': letter, 'image': f'signs/{image_name}'})
    return signs

model = load_model()
landmarker = prepare_detector() if model else None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/simulate')
def simulate():
    return render_template('simulate.html', letters=SIGN_LETTERS, model_ready=(model is not None))


@app.route('/dictionary')
def dictionary():
    signs = build_sign_list()
    return render_template('dictionary.html', signs=signs)


@app.route('/capture')
def capture():
    return render_template('capture.html')


@app.route('/learn')
def learn():
    return render_template('learn.html')


@app.route('/predict', methods=['POST'])
def predict():
    if model is None or landmarker is None:
        return jsonify({'error': 'Model belum tersedia.'}), 400

    data = request.get_json(silent=True) or {}
    image_data = data.get('image')
    if not image_data:
        return jsonify({'error': 'Tidak ada data gambar.'}), 400

    try:
        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except Exception:
        return jsonify({'error': 'Gagal memproses gambar.'}), 400

    if frame is None:
        return jsonify({'error': 'Gambar tidak valid.'}), 400

    def classify_input(input_frame):
        mp_image = frame_to_image(input_frame)
        result = landmarker.detect(mp_image)

        if not result.hand_landmarks:
            return None

        hand = result.hand_landmarks[0]
        landmarks = [(lm.x, lm.y, lm.z) for lm in hand]
        features = landmarks_to_features(landmarks)
        if features is None:
            return None

        prediction = model.predict([features])[0]
        confidence_value = None
        recognized_flag = True

        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba([features])[0]
            confidence_value = float(probabilities.max())
            recognized_flag = confidence_value >= 0.50

        return {
            'letter': str(prediction),
            'confidence': confidence_value,
            'recognized': recognized_flag,
        }

    candidates = []
    normal_result = classify_input(frame)
    flipped_result = classify_input(cv2.flip(frame, 1))

    if normal_result is not None:
        candidates.append(normal_result)
    if flipped_result is not None:
        candidates.append(flipped_result)

    if candidates:
        best = max(candidates, key=lambda item: item['confidence'] if item['confidence'] is not None else 0.0)
        letter = best['letter']
        confidence = f"{best['confidence']:.2f}" if best['confidence'] is not None else None
        recognized = best['recognized']
    else:
        letter = 'Tidak terdeteksi'
        confidence = None
        recognized = False

    response = {'letter': letter, 'recognized': recognized}
    if confidence is not None:
        response['confidence'] = confidence
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
