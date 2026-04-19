# app/routes_app.py
from dbm import sqlite3

from flask import render_template, request, redirect, url_for, flash
from app import app, get_db_connection

@app.route('/')
def index():
    # Redirect default către dashboard
    return redirect(url_for('dashboard'))
@app.route('/dashboard')
def dashboard():
    user_id = request.cookies.get('user_id')
    
    # VULNERABILITATE: Citim rolul direct din cookie-ul care poate fi modificat
    role_from_cookie = request.cookies.get('role', 'USER')

    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return redirect(url_for('logout'))

    # VULNERABILITATE (Privilege Escalation): Daca utilizatorul a modificat cookie-ul 
    # în "MANAGER", îi dăm acces la toate tichetele.
    if role_from_cookie == 'MANAGER':
        tickets = conn.execute('SELECT * FROM tickets').fetchall()
    else:
        tickets = conn.execute('SELECT * FROM tickets WHERE owner_id = ?', (user_id,)).fetchall()
        
    conn.close()

    # Trimitem rolul falsificat către frontend
    return render_template('dashboard.html', user=user, tickets=tickets, current_role=role_from_cookie)

# VULNERABILITATE (Missing Function Level Access Control / IDOR)
@app.route('/change_status/<int:ticket_id>', methods=['POST'])
def change_status(ticket_id):
    # ATENȚIE: Aici nu verificăm DACĂ utilizatorul este măcar logat
    # și nu verificăm DACĂ are rolul de MANAGER în baza de date!
    # Oricine știe acest URL poate trimite o cerere POST și va funcționa.
    
    new_status = request.form['status']
    
    conn = get_db_connection()
    conn.execute('UPDATE tickets SET status = ? WHERE id = ?', (new_status, ticket_id))
    conn.commit()
    conn.close()

    flash('Status schimbat!')
    return redirect(url_for('dashboard'))


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

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    user_id = request.cookies.get('user_id')
    role = request.cookies.get('role', 'USER')

    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    # VULNERABILITATE CRITICĂ: SQL Injection (Concatenare directă de string-uri)
    # Aici NU folosim "query parametrizat". Avem încredere oarbă în ce scrie utilizatorul.
    sql_query = f"SELECT * FROM tickets WHERE title LIKE '%{query}%' OR description LIKE '%{query}%'"
    
    try:
        tickets = conn.execute(sql_query).fetchall()
    except sqlite3.Error as e:
        # VULNERABILITATE (Information Disclosure): Arătăm eroarea exactă de DB atacatorului
        flash(f"Eroare Bază de Date: {e}") 
        tickets = []

    conn.close()
    
    # Returnăm la același dashboard vulnerabil
    return render_template('dashboard.html', user=user, tickets=tickets, current_role=role)