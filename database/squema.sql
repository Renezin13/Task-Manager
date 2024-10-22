-- Criação do banco de dados
CREATE DATABASE db_taskmanager;

-- Seleção do banco de dados criado
USE db_taskmanager;

-- Criação da tabela de Usuários
CREATE TABLE tb_usuarios (
    usr_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    usr_nome VARCHAR(90),
    usr_email TEXT,
    usr_senha TEXT
);

-- Criação da tabela de Tarefas
CREATE TABLE tb_tarefas (
    tar_id INT AUTO_INCREMENT PRIMARY KEY,           -- ID único da tarefa
    tar_titulo VARCHAR(255) NOT NULL, 
    tar_descricao VARCHAR(255) NOT NULL,             -- Descrição da tarefa
    tar_data_criacao DATE NOT NULL DEFAULT CURRENT_DATE, -- Data de criação da tarefa
    tar_data_limite DATE NOT NULL,                   -- Data limite da tarefa
    tar_status ENUM('Concluída', 'Em andamento', 'Pendente') DEFAULT 'Pendente', -- Status da tarefa
    tar_prioridade ENUM('Baixa', 'Média', 'Alta') DEFAULT 'Média',  -- Prioridade da tarefa
    tar_categoria VARCHAR(50),                        -- Categoria da tarefa (opcional)
    tar_data_conclusao DATE,                         -- Data de conclusão da tarefa (opcional)
    usr_id INT,                                      -- ID do usuário associado à tarefa
    FOREIGN KEY (usr_id) REFERENCES tb_usuarios(usr_id) -- Chave estrangeira referenciando usuários
);
