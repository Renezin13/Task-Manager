from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Task, User
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETO'

# Configuração do banco de dados
DATABASE_URL = "sqlite:///db_taskmanager.sqlite"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Inicializar o banco de dados
Base.metadata.create_all(bind=engine)

# Configuração do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    session = SessionLocal()
    user = session.query(User).get(int(user_id))  # Convertendo para int se necessário
    session.close()
    return user


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        session = SessionLocal()
        user = session.query(User).filter(User.email == email).first()
        session.close()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Email ou senha incorretos', 'danger')

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        session = SessionLocal()
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            flash('Esse email já está cadastrado!', 'error')
            session.close()
            return render_template('register.html')

        senha_hashed = generate_password_hash(senha)
        new_user = User(nome=nome, email=email, senha=senha_hashed)
        session.add(new_user)
        session.commit()
        session.close()

        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/dash')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/criar-tarefa', methods=['GET', 'POST'])
@login_required
def criar_tarefa():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prazo_str = request.form['prazo']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        status = request.form['status']

        # Converter 'prazo' para um objeto datetime (assumindo o formato YYYY-MM-DD)
        prazo = datetime.strptime(prazo_str, "%Y-%m-%d").date() if prazo_str else None

        session = SessionLocal()
        nova_tarefa = Task(
            titulo=titulo,
            descricao=descricao,
            prazo=prazo,
            prioridade=prioridade,
            categoria=categoria,
            status=status,
            usr_id=current_user.id
        )
        session.add(nova_tarefa)
        session.commit()
        session.close()

        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('addTask.html')



@app.route('/editar-tarefa/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id):
    session = SessionLocal()
    tarefa = session.query(Task).filter(Task.id == id, Task.usr_id == current_user.id).first()

    if request.method == 'POST':
        if tarefa:
            tarefa.titulo = request.form['titulo']
            tarefa.descricao = request.form['descricao']
            
            # Converte prazo de string para datetime.date
            prazo_str = request.form['prazo']
            if prazo_str:
                try:
                    tarefa.prazo = datetime.strptime(prazo_str, "%Y-%m-%d").date()
                except ValueError:
                    flash("Data de prazo inválida!", "danger")
                    session.close()
                    return redirect(url_for('editar_tarefa', id=id))

            tarefa.prioridade = request.form['prioridade']
            tarefa.categoria = request.form['categoria']
            tarefa.status = request.form['status']

            session.commit()
            session.close()

            flash('Tarefa atualizada com sucesso!', 'success')
            return redirect(url_for('dashboard'))

    if not tarefa:
        flash('Tarefa não encontrada.', 'danger')
        session.close()
        return redirect(url_for('dashboard'))

    session.close()
    return render_template('editar_tarefa.html', tarefa=tarefa)
    

@app.route('/tasks')
@login_required
def tasks():
    session = SessionLocal()
    query = session.query(Task).filter(Task.usr_id == current_user.id)

    # Aplicar filtros
    status = request.args.get('status')
    if status:
        if status == "1":
            status_mapped = "Concluída"
        elif status == "2":
            status_mapped = "Em andamento"
        elif status == "3":
            status_mapped = "Pendente"
        else:
            status_mapped = None

        if status_mapped:
            query = query.filter(Task.status == status_mapped)

    data_criacao = request.args.get('dataCriacao')
    if data_criacao:
        try:
            data_criacao = datetime.strptime(data_criacao, "%Y-%m-%d").date()
            query = query.filter(Task.data_criacao == data_criacao)
        except ValueError:
            flash("Data de criação inválida!", "danger")

    data_limite = request.args.get('dataLimite')
    if data_limite:
        try:
            data_limite = datetime.strptime(data_limite, "%Y-%m-%d").date()
            query = query.filter(Task.prazo <= data_limite)
        except ValueError:
            flash("Data limite inválida!", "danger")

    prioridade = request.args.get('prioridade')
    if prioridade:
        query = query.filter(Task.prioridade == prioridade)

    descricao = request.args.get('descricao')
    if descricao:
        query = query.filter(Task.descricao.like(f"%{descricao}%"))

    categoria = request.args.get('categoria')
    if categoria:
        query = query.filter(Task.categoria == categoria)

    tasks = query.all()
    session.close()

    # Mapeamento de prioridades e categorias
    prioridade_map = {"1": "Baixa", "2": "Média", "3": "Alta"}
    categoria_map = {"1": "Trabalho", "2": "Estudo", "3": "Pessoal"}

    return jsonify(tasks=[{
        'id': task.id,
        'title': task.titulo,
        'description': task.descricao,
        'creation_date': task.data_criacao.strftime("%Y-%m-%d") if task.data_criacao else None,
        'due_date': task.prazo.strftime("%Y-%m-%d") if task.prazo else None,
        'priority': prioridade_map.get(task.prioridade, task.prioridade),  # Mapeia a prioridade
        'category': categoria_map.get(task.categoria, task.categoria),  # Mapeia a categoria
        'status': task.status,
    } for task in tasks])

@app.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    session = SessionLocal()
    task = session.query(Task).filter(Task.id == id, Task.usr_id == current_user.id).first()

    if task:
        session.delete(task)
        session.commit()

    session.close()
    return jsonify(success=True), 204

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)