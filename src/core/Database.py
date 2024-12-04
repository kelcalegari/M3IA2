import sqlite3
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_table()

    def _connect(self):
        """Conecta ao banco de dados SQLite."""
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        """Cria a tabela 'users' se ainda não existir."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            """)
            conn.commit()

    def insert_user(self, name):
        """Insere um novo usuário no banco de dados."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
                conn.commit()
                return cursor.lastrowid  # Retorna o ID do usuário inserido
        except sqlite3.Error as e:
            print(f"Erro ao inserir usuário: {e}")
            return None

    def get_all_users(self):
        """Retorna todos os usuários cadastrados."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                return cursor.fetchall()  # Retorna lista de tuplas (id, name)
        except sqlite3.Error as e:
            print(f"Erro ao obter usuários: {e}")
            return []

    def get_user_name(self, user_id):
        """Retorna o nome do usuário pelo ID."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]  # Retorna apenas o nome
                return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar nome do usuário: {e}")
            return None

    def has_users(self):
        """Verifica se existem usuários cadastrados."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error as e:
            print(f"Erro ao verificar usuários: {e}")
            return False
