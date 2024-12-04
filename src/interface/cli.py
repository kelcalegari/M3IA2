import os
from src.core.FaceCapture import FaceCapture
from src.core.FaceRecognizer import FaceRecognizer
from src.core.FaceTrainer import FaceTrainer
from src.core.Database import Database

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), '../../database.sqlite')

# Inicializar banco de dados
db = Database(DB_PATH)

def menu():
    while True:
        print("\nMenu:")
        print("1. Capturar imagens para novo usuário")
        print("2. Treinar modelo")
        print("3. Fazer login")
        print("4. Listar usuários cadastrados")
        print("5. Sair")
        choice = input("Escolha uma opção: ")

        if choice == '1':
            name = input("Digite o nome do usuário: ")
            user_id = db.insert_user(name)  # Salva no banco e retorna o ID
            print(f"Usuário '{name}' cadastrado com ID: {user_id}")
            capture = FaceCapture()
            capture.capture_faces(user_id)
        elif choice == '2':
            trainer = FaceTrainer(os.path.join(os.path.dirname(__file__), '../../dataset'))
            trainer.load_images()
            trainer.train_model()
        elif choice == '3':
            recognizer = FaceRecognizer()
            recognizer.load_model()
            recognizer.recognize_face()
        elif choice == '4':
            users = db.get_all_users()
            if users:
                print("\nUsuários cadastrados:")
                for user in users:
                    print(f"ID: {user[0]}, Nome: {user[1]}")
            else:
                print("Nenhum usuário cadastrado.")
        elif choice == '5':
            print("Encerrando...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
