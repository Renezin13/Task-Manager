import mysql.connector
from flask_login import UserMixin

def obter_conexao():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_TaskManager"
    )   


class Task:
    def __init__(self, id, titulo, descricao, data_criacao, prazo, prioridade, categoria, usr_id):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.data_criacao = data_criacao
        self.prazo = prazo
        self.prioridade = prioridade
        self.categoria = categoria
        self.usr_id = usr_id

    @staticmethod
    def create(titulo, descricao, data_limite, prioridade, categoria=None, status='Pendente', user_id=None):
        if categoria == "1":
            categoria = "Trabalho"
        elif categoria == "2":
            categoria = "Estudo"
        elif categoria == "3":
            categoria = "Pessoal"
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(""" 
            INSERT INTO tb_tarefas (tar_titulo, tar_descricao, tar_data_limite, tar_prioridade, tar_categoria, tar_status, usr_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (titulo, descricao, data_limite, prioridade, categoria, status, user_id))
        print(categoria)
        conexao.commit()
        cursor.close()
        conexao.close()

    @staticmethod
    def get_user_tasks(user_id, status=None, data_criacao=None, data_limite=None, prioridade=None, descricao=None, categoria=None):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        query = "SELECT * FROM tb_tarefas WHERE usr_id = %s"
        params = [user_id]

        if status:
            query += " AND tar_status = %s"
            params.append(status)

        if data_criacao:
            query += " AND tar_data_criacao = %s"  # ajuste se o nome da coluna for diferente
            params.append(data_criacao)

        if data_limite:
            query += " AND tar_data_limite = %s"
            params.append(data_limite)

        if prioridade:
            query += " AND tar_prioridade = %s"
            params.append(prioridade)

        if descricao:
            query += " AND tar_descricao LIKE %s"
            params.append(f"%{descricao}%")

        if categoria:
            query += " AND tar_categoria = %s"
            params.append(categoria)

        cursor.execute(query, params)
        tasks = cursor.fetchall()
        cursor.close()
        conexao.close()
        return tasks


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