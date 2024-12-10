import os
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from collections import Counter

from src.core.Database import Database


class FaceRecognizer:
    def __init__(self, root, model_path=os.path.join( "models", "face_model.yml"),
                 cascade_path=cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
                 db_path=os.path.join(os.path.dirname(__file__), '../database.sqlite')):
        self.root = root
        self.model_path = model_path
        self.cascade_path = cascade_path
        self.db = Database(db_path)
        self.running = False
        self.video_capture = None
        self.canvas = None
        self.frame_id = None

    def load_model(self):
        """Carrega o modelo e os dados necessários."""
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(self.model_path)

    def recognize_face_for_duration(self, duration=10):
        """
        Realiza reconhecimento facial por um período especificado e retorna o ID do usuário mais frequente.
        :param duration: Tempo em segundos para capturar frames.
        :return: ID do usuário mais frequente ou None.
        """
        if self.running:  # Evita múltiplas execuções
            return None

        self.running = True
        self.video_capture = cv2.VideoCapture(0)

        if not self.video_capture.isOpened():
            print("Erro ao abrir a câmera.")
            self.running = False
            return None

        recognized_ids = []  # Lista para armazenar os IDs reconhecidos
        start_time = cv2.getTickCount()  # Tempo inicial
        fps = cv2.getTickFrequency()  # Frequência de ticks por segundo

        while (cv2.getTickCount() - start_time) / fps < duration:
            ret, frame = self.video_capture.read()
            if not ret:
                break

            # Converte para escala de cinza para detecção de faces
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detecta faces
            faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                face_id, confidence = self.recognizer.predict(gray_frame[y:y + h, x:x + w])
                if confidence < 50:  # Apenas IDs com confiança alta são adicionados
                    recognized_ids.append(face_id)

                # Opcional: desenhar retângulos no frame para feedback visual
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Opcional: exibir o frame em uma janela separada
            cv2.imshow("Reconhecimento Facial", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.running = False
        self.video_capture.release()
        cv2.destroyAllWindows()

        # Determina o ID mais frequente
        if recognized_ids:
            most_common_user = Counter(recognized_ids).most_common(1)[0][0]
            return most_common_user
        return None

    def recognize_face_once(self):
        """
        Realiza uma única iteração de reconhecimento facial e retorna o ID do usuário com a maior confiança.
        :return: ID do usuário reconhecido ou None se não houver reconhecimento válido.
        """
        if not self.video_capture or not self.video_capture.isOpened():
            self.video_capture = cv2.VideoCapture(0)

        if not self.video_capture.isOpened():
            print("Erro ao abrir a câmera.")
            return None

        ret, frame = self.video_capture.read()
        if not ret:
            print("Erro ao capturar o frame.")
            return None

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_id, confidence = self.recognizer.predict(gray_frame[y:y + h, x:x + w])
            if confidence < 50:  # Retorna o primeiro usuário com confiança aceitável
                return face_id

        return None  # Retorna None se nenhuma face válida foi reconhecida

    def stop_recognition(self):
        """Para o reconhecimento facial e libera recursos."""
        self.running = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        if self.canvas:
            self.canvas.pack_forget()
            self.canvas = None
        cv2.destroyAllWindows()
