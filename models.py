from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker 
from datetime import datetime

# Configuração do SQLAlchemy
DATABASE_URL = "sqlite:///db_taskmanager.sqlite"
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'tb_usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="user")

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):  # Método necessário para Flask-Login
        return str(self.id)

    @staticmethod
    def get_user_by_id(session, user_id):
        return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(session, email):
        return session.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(session, email, senha, nome):
        new_user = User(email=email, senha=senha, nome=nome)
        session.add(new_user)
        session.commit()

class Task(Base):
    __tablename__ = 'tb_tarefas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=datetime.now, nullable=False)
    prazo = Column(DateTime, nullable=True)
    prioridade = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    status = Column(String, default='Pendente')
    usr_id = Column(Integer, ForeignKey('tb_usuarios.id'))

    user = relationship("User", back_populates="tasks")

    @staticmethod
    def create_task(session, titulo, descricao, data_limite, prioridade, categoria=None, status='Pendente', user_id=None):
        if categoria == "1":
            categoria = "Trabalho"
        elif categoria == "2":
            categoria = "Estudo"
        elif categoria == "3":
            categoria = "Pessoal"

        new_task = Task(
            titulo=titulo,
            descricao=descricao,
            data_criacao=datetime.now(),
            prazo=data_limite,
            prioridade=prioridade,
            categoria=categoria,
            status=status,
            usr_id=user_id
        )
        session.add(new_task)
        session.commit()

    @staticmethod
    def get_user_tasks(session, user_id, **filters):
        query = session.query(Task).filter(Task.usr_id == user_id)

        if 'status' in filters and filters['status']:
            query = query.filter(Task.status == filters['status'])

        if 'data_criacao' in filters and filters['data_criacao']:
            query = query.filter(Task.data_criacao == filters['data_criacao'])

        if 'data_limite' in filters and filters['data_limite']:
            query = query.filter(Task.prazo == filters['data_limite'])

        if 'prioridade' in filters and filters['prioridade']:
            query = query.filter(Task.prioridade == filters['prioridade'])

        if 'descricao' in filters and filters['descricao']:
            query = query.filter(Task.descricao.like(f"%{filters['descricao']}%"))

        if 'categoria' in filters and filters['categoria']:
            query = query.filter(Task.categoria == filters['categoria'])

        return query.all()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
