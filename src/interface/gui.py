import os
import cv2
import time
import shutil
from collections import Counter
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox


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

        # Dimensões da janela
        largura_janela = 500
        altura_janela = 400

        # Calcula o centro horizontal da tela
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()

        # Calcula a posição horizontal (centro) e vertical (topo)
        pos_x = int((largura_tela - largura_janela) / 2)
        pos_y = 0  # Alinha no topo

        # Define a geometria da janela
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

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


#primeira tela

    def create_main_menu(self):
        """Cria o menu principal."""
        # Verifica se o dataset está vazio
        if self.is_dataset_empty():
            self.open_post_login_window()
            return  # Sai da função para evitar renderizar esta tela

        # Continua para criar o menu principal se o dataset não estiver vazio
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()
        self.show_message(f"Você não está autenticado", "blue")

        # Título
        tk.Label(self.current_frame, text="Sistema de Reconhecimento Facial", font=("Arial", 16)).pack(pady=10)

        # Botões
        tk.Button(self.current_frame, text="Login", command=lambda: self.show_instructions("login"), width=30).pack(pady=10)
        tk.Button(self.current_frame, text="Sair", command=self.root.quit, width=30).pack(pady=10)

    def open_settings(self):
        """Abre a interface de configurações."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        # tk.Label(self.current_frame, text="Configurações", font=("Arial", 16)).pack(pady=10)
        
        # Botão para apagar dados
        tk.Button(self.current_frame, text="Apagar Dataset", command=self.apagar_dados_ui, width=30).pack(pady=10)
        
        # Botão para voltar
        tk.Button(self.current_frame, text="Voltar", command=self.open_post_login_window, width=30).pack(pady=10)



    def apagar_dados_ui(self):
        """Interface para apagar dados."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=10)

        tk.Label(self.current_frame, text="Apagar Dados", font=("Arial", 16)).pack(pady=10)

        progress_bar = ttk.Progressbar(self.current_frame, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=10)

        def executar_apagar():
            pasta = os.path.normpath("C:/Users/Caio Soares/Documents/Visual Studio 2024/M3IA2/M3IA2/dataset")

            try:
                # Limpa o banco de dados
                self.db.delete_all_users()

                # Remove o conteúdo da pasta
                if os.path.exists(pasta):
                    itens_pasta = [os.path.join(pasta, item) for item in os.listdir(pasta)]
                    total_itens = len(itens_pasta)
                    progress_bar['maximum'] = total_itens + 100  # Inclui a barra do banco

                    progresso = 0
                    for item in itens_pasta:
                        if os.path.isfile(item) or os.path.islink(item):
                            os.remove(item)  # Remove arquivos
                        elif os.path.isdir(item):
                            shutil.rmtree(item)  # Remove subpastas
                        progresso += 1
                        progress_bar['value'] = progresso
                        progress_bar.update()

                # Simula progresso para o banco
                for i in range(progresso, progresso + 101):
                    progress_bar['value'] = i
                    progress_bar.update()
                    time.sleep(0.02)

                # Exibição de sucesso
                messagebox.showinfo("Sucesso", "Banco de dados e conteúdo da pasta limpos com sucesso!")
                self.create_main_menu()

            except Exception as e:
                # Exibição de erro
                messagebox.showerror("Erro", f"Erro ao limpar dados: {e}")
                self.create_main_menu()

        tk.Button(self.current_frame, text="Confirmar Deleção", command=executar_apagar, width=30).pack(pady=10)
        tk.Button(self.current_frame, text="Voltar", command=self.open_settings, width=30).pack(pady=10)

    def clear_frame(self):
        """Remove widgets antigos antes de criar novos."""
        if self.current_frame:
            for widget in self.current_frame.winfo_children():
                widget.destroy()
            self.current_frame.destroy()
        self.current_frame = None  # Reset o frame


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

    def recognize_user_with_delay(self, delay=2):
        """Realiza o reconhecimento facial com um atraso."""
        try:
            self.clear_frame()
            self.current_frame = tk.Frame(self.root)
            self.current_frame.pack()

            # Adiciona uma barra de progresso
            progress_label = tk.Label(self.current_frame, text="Realizando leitura facial...", font=("Arial", 12))
            progress_label.pack(pady=10)
            progress_bar = ttk.Progressbar(self.current_frame, orient="horizontal", length=400, mode="determinate")
            progress_bar.pack(pady=10)

            self.face_recognizer = FaceRecognizer(self.root)
            self.face_recognizer.load_model()
            recognized_ids = []

            # Tempo inicial e frequência
            start_time = cv2.getTickCount()
            fps = cv2.getTickFrequency()

            # Configura a barra de progresso
            progress_bar['maximum'] = delay * 100
            elapsed_time = 0

            while elapsed_time < delay:
                elapsed_time = (cv2.getTickCount() - start_time) / fps
                progress_bar['value'] = elapsed_time * 100
                self.root.update_idletasks()

                user_id = self.face_recognizer.recognize_face_once()
                if user_id:
                    recognized_ids.append(user_id)

            if recognized_ids:
                return Counter(recognized_ids).most_common(1)[0][0]

        except Exception as e:
            self.show_message(f"Erro no reconhecimento facial: {e}", "red")

        return None



#segunda tela

    def open_post_login_window(self):
        """Abre a janela principal após a autenticação bem-sucedida."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        
        if self.is_dataset_empty():
            # Dataset vazio: Apenas opção de cadastrar novo usuário
            self.show_message("", "green")
            tk.Label(self.current_frame, text=f"Bem-vindo ao Sistema!", font=("Arial", 16)).pack(pady=10)
            tk.Label(self.current_frame, text="O sistema não possui usuários cadastrados.", font=("Arial", 12)).pack(pady=5)
            tk.Button(self.current_frame, text="Cadastrar Novo Usuário", command=self.capture_faces_ui, width=30).pack(pady=10)
        else:
            tk.Label(self.current_frame, text=f"Bem-vindo ao Sistema {self.user_name}!", font=("Arial", 16)).pack(pady=10)

            # Dataset não está vazio: Exibe todas as opções
            tk.Button(self.current_frame, text="Cadastrar Novo Usuário", command=self.capture_faces_ui, width=30).pack(pady=10)
            tk.Button(self.current_frame, text="Listar Usuários", command=self.list_users_ui, width=30).pack(pady=10)
            # tk.Button(self.current_frame, text="Configurações", command=self.open_settings, width=30).pack(pady=10)
            tk.Button(self.current_frame, text="Desconectar", command=self.create_main_menu, width=30).pack(pady=10)
            tk.Button(self.current_frame, text="Sair", command=self.root.quit, width=30).pack(pady=10)

    def capture_faces_ui(self):
        """Cria a interface de captura de imagens."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=10)

        tk.Label(self.current_frame, text="Informe o nome do usuário:", font=("Arial", 12)).pack(pady=5)
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

        tk.Button(self.current_frame, text="Iniciar Captura", command=lambda: self.show_instructions("cadastro"), width=20).pack(pady=10)
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
        if hasattr(self, "message_label") and self.message_label.winfo_exists():
            self.message_label.config(text=message, fg=color)
        else:
            print("Não foi possível exibir a mensagem: label inexistente.")


#funções auxiliares do dataset

    def is_dataset_empty(self):
        """Verifica se o dataset (banco de dados) está vazio."""
        return not self.db.has_users()

    def list_users_ui(self):
        """Abre uma nova janela para listar os usuários cadastrados."""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(pady=10)

        tk.Label(self.current_frame, text="Usuários Cadastrados", font=("Arial", 16)).pack(pady=10)

        # Obtém os usuários do banco de dados
        users = self.db.get_all_users()
        if users:
            for user_id, name in users:
                tk.Label(self.current_frame, text=f"ID: {user_id}, Nome: {name}", font=("Arial", 12)).pack(pady=5)
        else:
            tk.Label(self.current_frame, text="Nenhum usuário encontrado.", font=("Arial", 12)).pack(pady=5)

        tk.Button(self.current_frame, text="Apagar Dataset", command=self.apagar_dados_ui, width=30).pack(pady=10)
        tk.Button(self.current_frame, text="Voltar", command=self.open_post_login_window, width=20).pack(pady=10)

    def show_instructions(self, action):
        """Exibe um popup com instruções e pergunta ao usuário se deseja prosseguir."""
        instructions = (
            "Para uma boa captura facial, siga as instruções abaixo:\n\n"
            "1. Certifique-se de estar em um local bem iluminado.\n"
            "2. Mantenha o rosto centralizado na câmera.\n"
            "3. Remova quaisquer acessórios que possam obstruir o rosto (ex.: chapéus, óculos de sol).\n"
            "4. Mantenha uma expressão neutra durante a captura.\n\n"
            "Deseja prosseguir com a operação?"
        )
        if messagebox.askyesno("Instruções para Captura Facial", instructions):
            if action == "login":
                self.authenticate_user()
            elif action == "cadastro":
                self.capture_faces_ui()

