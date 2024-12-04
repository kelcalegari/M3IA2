import os
import cv2
from collections import Counter
from PIL import Image, ImageTk
import tkinter as tk

from src.core.Database import Database
from src.core.FaceRecognizer import FaceRecognizer
from src.core.FaceCapture import FaceCapture
from src.core.FaceTrainer import FaceTrainer


class FaceAppGUI:
    DB_PATH = os.path.join(os.path.dirname(__file__), '../../database.sqlite')

    def __init__(self, root):
        self.db = Database(self.DB_PATH)
        self.root = root
        self.root.title("Sistema de Reconhecimento Facial")
        self.root.geometry("500x400")
        self.current_frame = None
        # Inicializa a label de mensagens
        self.message_label = tk.Label(self.root, text="", fg="green", font=("Arial", 10))
        self.message_label.pack(pady=10)

        # Verifica se já existe usuário no banco de dados, se sim, tenta autenticar
        if self.db.has_users():
            self.create_main_menu()
        else:
            self.user_name = ""
            self.open_post_login_window()

    def create_main_menu(self):
        """Cria o menu principal."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        # Título
        tk.Label(self.current_frame, text="Sistema de Reconhecimento Facial", font=("Arial", 16)).pack(pady=10)

        # Botões
        tk.Button(self.current_frame, text="Login", command=self.authenticate_user, width=30).pack(pady=10)
        tk.Button(self.current_frame, text="Sair", command=self.root.quit, width=30).pack(pady=10)

        # Área de mensagens
        self.message_label = tk.Label(self.current_frame, text="", fg="green", font=("Arial", 10))
        self.message_label.pack(pady=10)

    def clear_frame(self):
        """Remove widgets antigos antes de criar novos."""
        if self.current_frame:
            for widget in self.current_frame.winfo_children():
                widget.destroy()
            self.current_frame.destroy()

    def authenticate_user(self):
        """Realiza a autenticação do usuário ao clicar no botão de login ou automaticamente."""
        user_id = self.recognize_user_with_delay()

        if user_id:
            self.user_name = self.db.get_user_name(user_id)
            if self.user_name:
                self.show_message(f"Bem-vindo, {self.user_name}!", "green")
                self.open_post_login_window()
            else:
                self.show_message("Usuário não encontrado. Tente novamente.", "red")
        else:
            self.show_message("Autenticação falhou. Nenhuma face válida reconhecida.", "red")

    def recognize_user_with_delay(self, delay=10):

        """
        Executa o reconhecimento facial por um período e autentica o usuário mais frequente.
        :param delay: Tempo em segundos para a autenticação.
        :return: ID do usuário mais frequente ou None.
        """
        self.face_recognizer = FaceRecognizer(self.root)
        self.face_recognizer.load_model()
        recognized_ids = []
        start_time = cv2.getTickCount()
        fps = cv2.getTickFrequency()

        while (cv2.getTickCount() - start_time) / fps < delay:
            user_id = self.face_recognizer.recognize_face_once()
            if user_id:
                recognized_ids.append(user_id)

        if recognized_ids:
            # Retorna o ID mais frequente
            return Counter(recognized_ids).most_common(1)[0][0]

        return None

    def open_post_login_window(self):
        """Abre a janela principal após a autenticação bem-sucedida."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        tk.Label(self.current_frame, text=f"Bem-vindo ao Sistema {self.user_name}!", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.current_frame, text="Cadastrar Novo Usuário", command=self.capture_faces_ui, width=30).pack(pady=10)
        tk.Button(self.current_frame, text="Sair", command=self.root.quit, width=30).pack(pady=10)

    def capture_faces_ui(self):
        """Cria a interface de captura de imagens."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=10)

        tk.Label(self.current_frame, text="Digite o nome do usuário:", font=("Arial", 12)).pack(pady=5)
        name_entry = tk.Entry(self.current_frame, font=("Arial", 12))
        name_entry.pack(pady=5)

        def process_capture():
            name = name_entry.get()
            if name:
                user_id = self.db.insert_user(name)
                if user_id:
                    self.face_capture = FaceCapture(self.root)
                    self.face_capture.start_capture(user_id, callback=self.train_model)
                else:
                    self.show_message("Erro ao inserir usuário no banco de dados.", "red")
            else:
                self.show_message("Nome não pode ser vazio.", "red")

        tk.Button(self.current_frame, text="Iniciar Captura", command=process_capture, width=20).pack(pady=10)
        tk.Button(self.current_frame, text="Voltar", command=self.create_main_menu, width=20).pack(pady=10)

    def train_model(self):
        """Treina o modelo de reconhecimento facial."""
        try:
            trainer = FaceTrainer(os.path.join(os.path.dirname(__file__), '../../dataset'))
            trainer.load_images()
            trainer.train_model()
            self.show_message("Modelo treinado com sucesso!", "green")
            self.create_main_menu()
        except Exception as e:
            self.show_message(f"Erro ao treinar o modelo: {e}", "red")

    def show_message(self, message, color="green"):
        """Exibe uma mensagem dinâmica na área designada."""
        self.message_label.config(text=message, fg=color)
