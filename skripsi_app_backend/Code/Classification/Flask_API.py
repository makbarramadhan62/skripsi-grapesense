# from sklearn.metrics import accuracy_score, classification_report
from flask import Flask, request, jsonify
import cv2
import numpy as np
import pandas as pd
import joblib
import os
from werkzeug.utils import secure_filename
from skimage.feature import greycomatrix, greycoprops


app = Flask(__name__)

# membuat folder untuk menampung gambar yang di upload dari apps
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Load model
nb = joblib.load('../Model/NB_Model_HSV_GLCM[0]4_5Label.pkl')


def preprocess_and_extract_features(image):
    # Load image
    # image = cv2.imread(image_path)

    # Crop image menjadi kotak (1:1)
    height, width, channels = image.shape
    if height > width:
        crop_size = width
        y = int((height - width) / 2)
        x = 0
    else:
        crop_size = height
        x = int((width - height) / 2)
        y = 0
    cropped_image = image[y:y+crop_size, x:x+crop_size]

    # Resize image
    resized_image = cv2.resize(cropped_image, (1080, 1080))

    # Convert image ke HSV
    hsv = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)

    # Perhitungan rata rata hsv
    mean_h, mean_s, mean_v = np.mean(hsv, axis=(0, 1))

    # Hitung matriks glcm
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    glcm = greycomatrix(image_gray, [5], [0],
                        levels=256, symmetric=True, normed=True)

    # Hitung fitur glcm
    correlation = greycoprops(glcm, 'correlation')[0][0]
    homogeneity = greycoprops(glcm, 'homogeneity')[0][0]
    contrast = greycoprops(glcm, 'contrast')[0][0]

    # Create feature array
    X = np.array([mean_h, mean_s, mean_v, correlation, homogeneity, contrast])

    return X


@app.route('/')
def home():
    return 'Welcome to API Grapesense!'


@app.route('/klasifikasi', methods=['POST'])
def classify():
    # Mendapatkan file dari request API
    image_file = request.files['image']

    # Menyimpan gambar ke folder uploads
    filename = secure_filename(image_file.filename)
    image_path = os.path.join('uploads', filename)
    image_file.save(image_path)

    # Membaca gambar dari file ke numpy array
    # image = cv2.imdecode(np.fromstring(
    #     image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    image = cv2.imread(image_path)

    # Melakukan pre processing dan ekstraksi fitur
    X = preprocess_and_extract_features(image)

    # Mengubah bentuk array
    X_reshaped = X.reshape(1, -1)

    # Membuat dataframe menggunakan nama fitur
    feature_names = ['H', 'S', 'V', 'correlation', 'homogeneity', 'contrast']
    X_new = pd.DataFrame(data=X_reshaped, columns=feature_names)

    # Predict label
    y_pred = nb.predict(X_new)

    # Hasil
    result = int(y_pred[0])

    # Print label
    print(f'Label: {y_pred[0]}')
    return jsonify({'Label': result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
