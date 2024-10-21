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
    tar_descricao VARCHAR(255) NOT NULL,             -- Descrição da tarefa
    tar_data_criacao DATE NOT NULL,                  -- Data de criação da tarefa
    tar_data_limite DATE NOT NULL,                   -- Data limite da tarefa
    tar_status ENUM('Concluída', 'Em andamento', 'Pendente') DEFAULT 'Pendente', -- Status da tarefa
    tar_prioridade ENUM('Baixa', 'Média', 'Alta') DEFAULT 'Média',  -- Prioridade da tarefa
    tar_categoria VARCHAR(50),                        -- Categoria da tarefa (opcional)
    tar_data_conclusao DATE                          -- Data de conclusão da tarefa (opcional)
);

-- Exemplos de inserção de dados
INSERT INTO tar_tarefas (tar_descricao, tar_data_criacao, tar_data_limite, tar_status, tar_prioridade, tar_categoria)
VALUES 
    ('Estudar para a prova de matemática', '2024-10-01', '2024-10-10', 'Pendente', 'Alta', 'Estudo'),
    ('Comprar materiais de escritório', '2024-10-05', '2024-10-12', 'Em andamento', 'Média', 'Trabalho'),
    ('Organizar a festa de aniversário', '2024-10-10', '2024-10-15', 'Pendente', 'Baixa', 'Pessoal'),
    ('Finalizar relatório trimestral', '2024-10-02', '2024-10-08', 'Concluída', 'Alta', 'Trabalho');
