import csv
import os
import cv2
from utils import (
    create_hand_landmarker,
    draw_hand_landmarks,
    frame_to_image,
    landmarks_to_features,
)

OUTPUT_FILE = os.path.join('data', 'landmarks.csv')
TARGET_SAMPLES = 100


def ensure_header(path, vector_length):
    if not os.path.exists(path):
        header = ['label'] + [f'f{i}' for i in range(vector_length)]
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)


def main():
    landmarker = create_hand_landmarker()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('Tidak dapat membuka webcam.')
        return

    while True:
        label = input('Masukkan huruf (A-Z) untuk dikumpulkan, lalu enter (kosong untuk keluar): ').strip().upper()
        if label == '':
            break
        if len(label) != 1 or not label.isalpha():
            print('Masukkan hanya satu huruf A-Z.')
            continue

        print(f'Pengambilan data untuk huruf: {label}. Tunjukkan satu tangan ke kamera.')
        count = 0

        while count < TARGET_SAMPLES:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            mp_image = frame_to_image(frame)
            result = landmarker.detect(mp_image)
            image = frame.copy()

            if result.hand_landmarks:
                hand = result.hand_landmarks[0]
                landmarks = [(lm.x, lm.y, lm.z) for lm in hand]
                features = landmarks_to_features(landmarks)
                if features is not None:
                    ensure_header(OUTPUT_FILE, len(features))
                    with open(OUTPUT_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([label] + features.tolist())
                    count += 1

                image = draw_hand_landmarks(image, hand)

            cv2.putText(
                image,
                f'Label: {label}  Sampel: {count}/{TARGET_SAMPLES}',
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            cv2.imshow('Capture Dataset - Tekan q untuk berhenti', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return

        print(f'Selesai menyimpan {count} sampel untuk huruf {label}.')

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
