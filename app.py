from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Task, User, obter_conexao


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETO'


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = User.get_by_email(email)

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

        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usr_email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing_user:
            # Exibe mensagem de erro sem redirecionar
            flash('Esse email já está cadastrado!', 'error')
            return render_template('register.html')

        senha_hashed = generate_password_hash(senha)
        
        # Insere o novo usuário
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tb_usuarios (usr_email, usr_senha, usr_nome) VALUES (%s, %s, %s)",
                       (email, senha_hashed, nome))
        conn.commit()
        cursor.close()
        conn.close()

        # Exibe mensagem de sucesso e redireciona para a tela de login
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
        prazo = request.form['prazo']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        status = request.form['status']  # Novo campo

        # Criar a tarefa no banco de dados
        Task.create(titulo, descricao, prazo, prioridade, categoria, status, current_user.id)

        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('addTask.html')


@app.route('/editar-tarefa/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id):
    # Recuperar a tarefa com o ID fornecido
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_tarefas WHERE tar_id = %s AND usr_id = %s", (id, current_user.id))
    tarefa = cursor.fetchone()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prazo = request.form['prazo']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        status = request.form['status']

        # Atualizar a tarefa no banco de dados
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tb_tarefas 
            SET tar_titulo = %s, tar_descricao = %s, tar_data_limite = %s, 
                tar_prioridade = %s, tar_categoria = %s, tar_status = %s 
            WHERE tar_id = %s AND usr_id = %s
        """, (titulo, descricao, prazo, prioridade, categoria, status, id, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    # Se a tarefa não for encontrada, redirecionar
    if tarefa is None:
        flash('Tarefa não encontrada.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('editar_tarefa.html', tarefa=tarefa)


@app.route('/tasks')
@login_required
def tasks():
    status = request.args.get('status')
    data_criacao = request.args.get('dataCriacao')
    data_limite = request.args.get('dataLimite')
    prioridade = request.args.get('prioridade')
    descricao = request.args.get('descricao')
    categoria = request.args.get('categoria')

    # Inicia a consulta
    query = f"SELECT * FROM tb_tarefas WHERE usr_id = {current_user.id}"
    lista = list()

    # Adiciona condições com base nos parâmetros recebidos
    if status:
        if status == "1":
            comandoS = "Concluída"
        elif status == "2":
            comandoS = "Em andamento"
        elif status == "3":
            comandoS = "Pendente"
        query += f" AND tar_status = '{comandoS}'"
    if data_criacao:
        query += f" AND tar_data_criacao = '{data_criacao}'"
        lista.append(data_criacao)
    if data_limite:
        query += f" AND tar_data_limite = '{data_limite}'"
        lista.append(data_limite)
    if prioridade:
        if prioridade == "1":
            comandoP = "Alta"
        elif prioridade == "2":
            comandoP = "Média"
        elif prioridade == "3":
            comandoP = "Baixa"
        query += f" AND tar_prioridade = '{comandoP}'"
        lista.append(prioridade)
    if descricao:
        query += f" AND tar_descricao LIKE '{descricao}'"
        lista.append(descricao)
    if categoria:
        if categoria == "1":
            comandoC = "Trabalho"
        elif categoria == "2":
            comandoC = "Estudo"
        elif categoria == "3":
            comandoC = "Pessoal"
        query += f" AND tar_categoria = '{comandoC}'"
        lista.append(categoria)

    # Executa a consulta com os parâmetros
    print(lista)
    print(query)
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute(query)
    user_tasks = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(tasks=[{
        'id': task[0],
        'title': task[1],
        'description': task[2],
        'creation_date': task[3],
        'due_date': task[4],
        'priority': task[6],
        'category': task[7],
        'status': task[5],
    } for task in user_tasks])


@app.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tb_tarefas WHERE tar_id = %s AND usr_id = %s", (id, current_user.id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(success=True), 204


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)