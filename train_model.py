import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from joblib import dump

DATA_PATH = os.path.join('data', 'landmarks.csv')
MODEL_PATH = 'model.pkl'


def main():
    if not os.path.exists(DATA_PATH):
        print('Data tidak ditemukan. Jalankan capture_dataset.py terlebih dahulu.')
        return

    df = pd.read_csv(DATA_PATH)
    if df.empty:
        print('File data kosong. Kumpulkan data lebih dulu.')
        return

    X = df.drop(columns=['label']).values
    y = df['label'].astype(str).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print('Akurasi pada data uji:', accuracy_score(y_test, y_pred))
    print('\nLaporan klasifikasi:')
    print(classification_report(y_test, y_pred, zero_division=0))

    dump(model, MODEL_PATH)
    print(f'Model tersimpan ke {MODEL_PATH}')


if __name__ == '__main__':
    main()
