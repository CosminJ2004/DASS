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