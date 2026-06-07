from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "getsemani_ecossistema_secret_secure_key"

def conectar_banco():
    return sqlite3.connect('igreja_web.db')

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS dizimos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fiel TEXT, valor REAL, ministerio TEXT, data TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, login TEXT, senha TEXT, cargo TEXT)''')
    
    cursor.execute("SELECT * FROM usuarios WHERE login = 'brayan'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (nome, login, senha, cargo) VALUES (?, ?, ?, ?)",
                       ("Brayan", "brayan", "1234", "ADMINISTRADOR"))
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form.get('login').lower().strip()
        user_senha = request.form.get('senha').strip()
        
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, cargo FROM usuarios WHERE login = ? AND senha = ?", (user_login, user_senha))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            session['usuario_nome'] = usuario[0]
            session['usuario_cargo'] = usuario[1]
            return redirect(url_for('dashboard'))
        else:
            flash("Login ou senha incorretos!", "erro")
            
    return render_template('login.html')

@app.route('/')
def dashboard():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
        
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT fiel, ministerio, valor, data FROM dizimos ORDER BY id DESC")
    historico = cursor.fetchall()
    
    cursor.execute("SELECT SUM(valor) FROM dizimos")
    total_caixa = cursor.fetchone()[0] or 0.0
    conn.close()
    
    return render_template('index.html', 
                           historico=historico, 
                           total_caixa=total_caixa, 
                           nome_usuario=session['usuario_nome'], 
                           cargo_usuario=session['usuario_cargo'])

@app.route('/lancar', methods=['POST'])
def lancar_entrada():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
        
    fiel = request.form.get('fiel').upper()
    valor = float(request.form.get('valor'))
    ministerio = request.form.get('ministerio')
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    conn = conectar_banco()
    conn.execute("INSERT INTO dizimos (fiel, valor, ministerio, data) VALUES (?, ?, ?, ?)",
                 (fiel, valor, ministerio, data))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/configuracoes')
def configuracoes():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))
    return render_template('configuracoes.html', nome_usuario=session['usuario_nome'], cargo_usuario=session['usuario_cargo'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_banco()
    app.run(debug=True)