import os
import cv2
import numpy as np
import tkinter as tk
class FaceTrainer:
    def __init__(self, dataset_dir, model_path=os.path.join( "models", "face_model.yml")):
        self.dataset_dir = dataset_dir
        self.model_path = model_path
        self.faces = []
        self.labels = []

    def load_images(self):
        for file in os.listdir(self.dataset_dir):

            if file.startswith("user_") and file.endswith(".jpg"):
                try:
                    user_id = int(file.split("_")[1])
                    img_path = os.path.join(self.dataset_dir, file)
                    face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if face_img is not None:
                        self.faces.append(face_img)
                        self.labels.append(user_id)
                except Exception as e:
                    print(f"Erro ao processar {file}: {e}")

    def train_model(self):
        if len(self.faces) > 0 and len(self.labels) > 0:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(self.faces, np.array(self.labels))
            recognizer.save(self.model_path)
            print("Modelo treinado e salvo.")
        else:
            print("Nenhuma imagem válida para treinamento.")

# Exemplo de uso
if __name__ == "__main__":

    recognizer = FaceTrainer(os.path.join(os.path.dirname(__file__), '../../dataset'))

    # Carregar as imagens do dataset
    recognizer.load_images()

    # Treinar o modelo se houver faces para treinar
    recognizer.train_model()
