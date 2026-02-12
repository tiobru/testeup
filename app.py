from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = '12345'

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': '123',
    'port': '5433'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ROTA PRINCIPAL - PÁGINA INICIAL
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inserir', methods=['POST'])
def inserir_nome():
    nome = request.form.get('nome')
    
    if not nome:
        flash('Nome é obrigatório!', 'error')
        return redirect(url_for('index'))
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # CORREÇÃO: Use o nome correto da tabela e coluna
        cursor.execute(
            "INSERT INTO nomes (nome) VALUES (%s) RETURNING id",
            (nome,)
        )
        
        id_inserido = cursor.fetchone()[0]
        conn.commit()
        
        flash(f'Nome "{nome}" inserido com sucesso! ID: {id_inserido}', 'success')
        return redirect(url_for('index'))
        
    except psycopg2.Error as e:
        conn.rollback()
        flash(f'Erro ao inserir: {e}', 'error')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Rota para ver todos os nomes
@app.route('/listar')
def listar_nomes():
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        # Usando RealDictCursor para acesso mais fácil aos dados
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # CORREÇÃO: Use o nome correto da tabela
        cursor.execute("SELECT id, nome, data_criacao FROM nomes ORDER BY id DESC")
        nomes = cursor.fetchall()
        
        return render_template('listar.html', nomes=nomes)
        
    except psycopg2.Error as e:
        flash(f'Erro ao listar: {e}', 'error')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)