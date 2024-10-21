from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, obter_conexao
import smtplib
import email.message


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETO'


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
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
            flash('Esse email já está cadastrado!', 'error')
            return redirect(url_for('register'))

        senha_hashed = generate_password_hash(senha)
        
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tb_usuarios (usr_email, usr_senha, usr_nome) VALUES (%s, %s, %s)",
                       (email, senha_hashed, nome))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Filtros para a listagem de tarefas
    filtro_status = request.form.get('filtroStatus', 'Todos')
    filtro_data_criacao = request.form.get('filtroDataCriacao')
    filtro_prazo = request.form.get('filtroPrazo')
    filtro_prioridade = request.form.get('filtroPrioridade', 'Todos')
    filtro_palavra_chave = request.form.get('filtroPalavraChave')
    filtro_categoria = request.form.get('filtroCategoria', 'Todos')

    query = "SELECT * FROM tb_tarefas WHERE 1=1"
    params = []

    # Aplicar filtros dinamicamente
    if filtro_status and filtro_status != 'Todos':
        query += " AND tar_status = %s"
        params.append(filtro_status)
    if filtro_data_criacao:
        query += " AND tar_data_criacao = %s"
        params.append(filtro_data_criacao)
    if filtro_prazo:
        query += " AND tar_data_limite = %s"
        params.append(filtro_prazo)
    if filtro_prioridade and filtro_prioridade != 'Todos':
        query += " AND tar_prioridade = %s"
        params.append(filtro_prioridade)
    if filtro_palavra_chave:
        query += " AND tar_descricao LIKE %s"
        params.append(f"%{filtro_palavra_chave}%")
    if filtro_categoria and filtro_categoria != 'Todos':
        query += " AND tar_categoria = %s"
        params.append(filtro_categoria)

    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute(query, params)
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()

    # Renderiza o template dashboard passando as tarefas
    return render_template('dashboard.html', tarefas=tarefas)


# Rota para criar uma nova tarefa
@app.route('/criar-tarefa', methods=['POST'])
@login_required
def criar_tarefa():
    descricao = request.form['descricao']
    data_criacao = request.form['dataCriacao']
    data_limite = request.form['dataLimite']

    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tb_tarefas (tar_descricao, tar_data_criacao, tar_data_limite)
        VALUES (%s, %s, %s)
    """, (descricao, data_criacao, data_limite))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Tarefa criada com sucesso!', 'success')
    return redirect(url_for('dashboard'))


# Rota para atualizar uma tarefa
@app.route('/atualizar-tarefa', methods=['POST'])
@login_required
def atualizar_tarefa():
    tarefa_id = request.form['tarefaId']
    nova_descricao = request.form.get('novaDescricao')
    status = request.form.get('status')
    novo_prazo = request.form.get('novoPrazo')

    conn = obter_conexao()
    cursor = conn.cursor()

    # Atualizando os campos que foram informados
    if nova_descricao:
        cursor.execute("UPDATE tb_tarefas SET tar_descricao = %s WHERE tar_id = %s", (nova_descricao, tarefa_id))
    if status:
        cursor.execute("UPDATE tb_tarefas SET tar_status = %s WHERE tar_id = %s", (status, tarefa_id))
    if novo_prazo:
        cursor.execute("UPDATE tb_tarefas SET tar_data_limite = %s WHERE tar_id = %s", (novo_prazo, tarefa_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Tarefa atualizada com sucesso!', 'success')
    return redirect(url_for('dashboard'))


# Rota para excluir uma tarefa
@app.route('/excluir-tarefa', methods=['POST'])
@login_required
def excluir_tarefa():
    tarefa_id = request.form['excluirId']

    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tb_tarefas WHERE tar_id = %s", (tarefa_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Tarefa excluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))


# Rota para listar e filtrar tarefas
@app.route('/listar-tarefas', methods=['GET', 'POST'])
@login_required
def listar_tarefas():
    filtro_status = request.form.get('filtroStatus', 'Todos')
    filtro_data_criacao = request.form.get('filtroDataCriacao')
    filtro_prazo = request.form.get('filtroPrazo')
    filtro_prioridade = request.form.get('filtroPrioridade', 'Todos')
    filtro_palavra_chave = request.form.get('filtroPalavraChave')
    filtro_categoria = request.form.get('filtroCategoria', 'Todos')

    query = "SELECT * FROM tb_tarefas WHERE 1=1"
    params = []

    # Aplicar filtros dinamicamente
    if filtro_status and filtro_status != 'Todos':
        query += " AND tar_status = %s"
        params.append(filtro_status)
    if filtro_data_criacao:
        query += " AND tar_data_criacao = %s"
        params.append(filtro_data_criacao)
    if filtro_prazo:
        query += " AND tar_data_limite = %s"
        params.append(filtro_prazo)
    if filtro_prioridade and filtro_prioridade != 'Todos':
        query += " AND tar_prioridade = %s"
        params.append(filtro_prioridade)
    if filtro_palavra_chave:
        query += " AND tar_descricao LIKE %s"
        params.append(f"%{filtro_palavra_chave}%")
    if filtro_categoria and filtro_categoria != 'Todos':
        query += " AND tar_categoria = %s"
        params.append(filtro_categoria)

    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute(query, params)
    tarefas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('listar_tarefas.html', tarefas=tarefas)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)