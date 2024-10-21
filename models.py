import mysql.connector
from flask_login import UserMixin

def obter_conexao():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_TaskManager"
    )   

class User(UserMixin):  
    def __init__(self, id, nome, email, senha):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha


    @staticmethod
    def get(user_id):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usr_id = %s", (user_id,))
        result = cursor.fetchone()
        conexao.close()
        if result:
            return User(result[0], result[1], result[2], result[3])
        return None


    @staticmethod
    def get_by_email(email):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usr_email = %s", (email,))
        result = cursor.fetchone()
        conexao.close()
        if result:
            return User(result[0], result[1], result[2], result[3])
        return None


    @staticmethod
    def create(email, senha, nome):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO tb_usuarios (usr_email, usr_senha, usr_nome) VALUES (%s, %s, %s)", (email, senha, nome))
        conexao.commit()
        conexao.close()


    @property
    def is_active(self):
        return True


    @property
    def is_authenticated(self):
        return True


    @property
    def is_anonymous(self):
        return False