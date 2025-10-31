import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# Inicializa a aplicação Flask
app = Flask(__name__)

# --- Configuração do Banco de Dados ---

# 1. Lê as variáveis de ambiente
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')

# 2. Cria a "String de Conexão"
# Formato: mysql+pymysql://USUARIO:SENHA@HOST/NOME_DO_BANCO
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'

# 3. Inicializa o SQLAlchemy
# 'db' agora é nosso objeto para interagir com o banco
db = SQLAlchemy(app)

# --- Definição do Modelo (Tabela) ---
class Task(db.Model):
    # __tablename__ é opcional, mas é uma boa prática
    # dizer explicitamente o nome da tabela no MySQL.
    __tablename__ = 'tasks' 
    
    # Coluna 1: ID
    # db.Integer = um número inteiro.
    # primary_key=True = Esta é a chave primária.
    id = db.Column(db.Integer, primary_key=True)
    
    # Coluna 2: Título
    # db.String(255) = um texto de até 255 caracteres.
    # nullable=False = Esta coluna não pode estar vazia.
    title = db.Column(db.String(255), nullable=False)
    
    # Coluna 3: Status
    # db.Boolean = Verdadeiro (True) ou Falso (False).
    # default=False = Se não dissermos nada, a tarefa começa como "não concluída".
    done = db.Column(db.Boolean, default=False)

# Define uma rota de "health check" (verificação de saúde)
# Isso é muito comum em DevOps para monitorar se a aplicação está "viva"
@app.route('/api/health')
def health_check():
    """Verifica se a API está funcionando."""
    # Retorna uma resposta simples em formato JSON
    return jsonify({"status": "ok", "message": "API está no ar!"})

# Define uma rota de exemplo para nossas tarefas
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Busca todas as tarefas no banco de dados."""
    
    # 1. Executa a consulta no banco
    #    Task.query.all() -> SELECT * FROM tasks;
    all_tasks_objects = Task.query.all()
    
    # 2. Converte os objetos para uma lista de dicionários
    tasks_list = []
    for task in all_tasks_objects:
        tasks_list.append({
            "id": task.id,
            "title": task.title,
            "done": task.done
        })

    return jsonify(tasks_list)

# --- Cria as tabelas no banco ---
# Isso verifica se o app está pronto e então cria as tabelas
# se elas ainda não existirem.
with app.app_context():
    db.create_all()

# Rota para ATUALIZAR uma tarefa existente (PUT)
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Atualiza uma tarefa existente."""
    
    # 1. Encontra a tarefa pelo ID.
    # O .get_or_404() é um atalho muito útil:
    # - Tenta encontrar a tarefa com o 'task_id'.
    # - Se não encontrar, ele para a execução e retorna um erro 404 (Not Found) automaticamente.
    task = Task.query.get_or_404(task_id)
    
    # 2. Pega os dados JSON enviados no corpo da requisição
    # (Precisamos ter importado 'request' do flask lá no topo do arquivo)
    data = request.json
    
    # 3. Atualiza os campos do objeto 'task' com os novos dados
    # Usamos 'data.get(..., ...)' para segurança:
    # - Ele tenta pegar o 'title' do JSON.
    # - Se o JSON não enviar um 'title', ele usa o valor que já estava lá (task.title).
    task.title = data.get('title', task.title)
    task.done = data.get('done', task.done)
    
    # 4. Salva (commita) as mudanças no banco de dados
    db.session.commit()
    
    # Retorna uma confirmação
    return jsonify({"message": "Tarefa atualizada com sucesso!"})

# Rota para CRIAR uma nova tarefa (POST)
@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Cria uma nova tarefa no banco de dados."""
    
    # 1. Pega os dados JSON enviados no corpo da requisição
    data = request.json
    
    # 2. Validação simples:
    #    Verifica se o campo 'title' foi enviado. Se não, retorna um erro 400.
    if not data or 'title' not in data:
        return jsonify({"message": "Erro: 'title' é obrigatório."}), 400

    # 3. Cria o novo objeto Task
    new_task = Task(
        title=data['title'],
        # O 'done' é opcional; se não for enviado, usará o 'default=False'
        # que definimos no nosso modelo (Task).
        done=data.get('done', False) 
    )
    
    # 4. Adiciona o novo objeto à sessão do banco
    db.session.add(new_task)
    
    # 5. Salva (commita) as mudanças no banco
    db.session.commit()
    
    # 6. Retorna uma resposta de sucesso (Código 201 = Created)
    return jsonify({"message": "Tarefa criada com sucesso!", "id": new_task.id}), 201

# Rota para DELETAR uma tarefa (DELETE)
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Deleta uma tarefa do banco de dados."""
    
    # 1. Encontra a tarefa pelo ID (ou retorna 404 se não existir)
    task = Task.query.get_or_404(task_id)
    
    # 2. Adiciona o objeto à sessão para ser deletado
    db.session.delete(task)
    
    # 3. Salva (commita) a deleção no banco
    db.session.commit()
    
    # 4. Retorna uma confirmação
    return jsonify({"message": "Tarefa deletada com sucesso!"})

# Permite que o servidor seja executado usando "python app.py"
if __name__ == '__main__':
    # O 'host="0.0.0.0"' é crucial para o Docker.
    # Ele faz o servidor Flask escutar em todas as interfaces de rede,
    # não apenas em 'localhost' (127.0.0.1).
    app.run(host='0.0.0.0', port=5000, debug=True)