# app/routes_app.py
from flask import render_template, request, redirect, url_for
from app import app, get_db_connection

@app.route('/')
def index():
    # Redirect default către dashboard
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Citim sesiunea vulnerabilă din cookie [cite: 14]
    user_id = request.cookies.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return redirect(url_for('logout'))

    # Preluăm tichetele pentru a le afișa pe dashboard
    tickets = conn.execute('SELECT * FROM tickets').fetchall()
    conn.close()

    return render_template('dashboard.html', user=user, tickets=tickets)

@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    # Identificăm userul din cookie-ul vulnerabil
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        severity = request.form.get('severity', 'LOW')

        # VULNERABILITATE: Nu există nicio curățare (sanitizare) a input-ului.
        # Atacatorul poate introduce cod <script> direct aici.
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO tickets (title, description, severity, owner_id) VALUES (?, ?, ?, ?)',
            (title, description, severity, user_id)
        )
        conn.commit()
        conn.close()

        flash('Tichet creat cu succes!')
        return redirect(url_for('dashboard'))

    return render_template('create_ticket.html')