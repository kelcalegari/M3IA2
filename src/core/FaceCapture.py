import os

import cv2
from PIL import Image, ImageTk
import tkinter as tk
class FaceCapture:
    def __init__(self, root, dataset_dir=os.path.join(os.path.dirname(__file__), '../../dataset'),
                 face_cascade_path=cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'):
        self.root = root
        self.dataset_dir = dataset_dir
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.cap = cv2.VideoCapture(0)
        self.running = False
        self.canvas = None

    def start_capture(self, user_id, num_images=100, callback=None):
        """Inicia a captura de imagens integradas ao Tkinter."""
        self.running = True
        self.callback = callback
        self.count = 0
        self.root.geometry("500x650")

        # Cria um canvas para exibir o feed da câmera
        self.canvas = tk.Canvas(self.root, width=640, height=480)
        self.canvas.pack()

        def update_frame():

            if not self.running:
                return

            ret, frame = self.cap.read()
            if ret:
                # Converte o frame para exibir no Tkinter
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    if self.count < num_images:
                        face = gray_frame[y:y + h, x:x + w]
                        cv2.imwrite(f"{self.dataset_dir}/user_{user_id}_{self.count}.jpg", face)
                        self.count += 1

                # Converte o frame BGR para RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.image = imgtk

            if self.count >= num_images:
                self.stop_capture()
                print("Captura finalizada.")
                if self.callback:  # Chama o callback para voltar ao menu
                    self.root.geometry("500x400")
                    self.callback()
                return

            # Atualiza o frame a cada 10ms
            self.root.after(10, update_frame)

        update_frame()

    def stop_capture(self):
        """Para a captura e libera os recursos."""
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        if self.canvas:
            self.canvas.destroy()
