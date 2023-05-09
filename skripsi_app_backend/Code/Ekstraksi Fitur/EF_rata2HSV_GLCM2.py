import os
import cv2
import csv
import numpy as np
from skimage.feature import greycomatrix, greycoprops

x = 0
glcm_properties = ['dissimilarity', 'correlation',
                   'homogeneity', 'contrast', 'ASM', 'energy', ]
angles = [0, 45, 90, 135]

# membuka file CSV untuk menyimpan hasil ekstraksi fitur
with open('../CSV/HSV_GLCM/HSV_GLCM_Training2.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        ['label', 'R', 'G', 'B'] + [f'{prop} {angle}' for prop in glcm_properties for angle in angles])

    # melakukan ekstraksi fitur pada setiap folder
    for root, dirs, files in os.walk('../Dataset/DataSet_Training'):

        x = x+1
        # mengambil nama folder terakhir dari root
        label = root.split('\\')[-1]

        # mengambil semua file gambar di dalam folder
        image_files = [f for f in files if f.endswith('.jpg')]

        # melakukan ekstraksi fitur pada setiap gambar
        for image_file in image_files:
            # membaca gambar
            image = cv2.imread(os.path.join(root, image_file))

            # mengubah gambar ke dalam format HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Hitung nilai rata-rata intensitas merah, hijau, dan biru
            mean_h, mean_s, mean_v = np.mean(hsv, axis=(0, 1))

            # Hitung matriks glcm
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            glcm = greycomatrix(image_gray, distances=[5], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
                                levels=256, symmetric=True, normed=True)

            # Hitung fitur glcm
            feature = []
            glcm_props = [
                propery for name in glcm_properties for propery in greycoprops(glcm, name)[0]]
            for item in glcm_props:
                feature.append(item)

            row = [(x-1), mean_h, mean_s, mean_v] + feature[:]
            writer.writerow(row)

# Menutup file CSV
csvfile.close()
