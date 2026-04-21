# app/routes_app.py
from flask import render_template, redirect, url_for, session, request, flash
from app import app, get_db_connection, log_audit

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cookie_token = session.get('session_token') # Ce ne dă browserul

    conn = get_db_connection()
    # Citim și session_token din baza de date
    user = conn.execute('SELECT id, email, role, locked, session_token FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Dacă token-ul din BD nu se potrivește cu cel din browser, e clar că s-a dat logout anterior!
    if not user or user['locked'] or user['session_token'] != cookie_token:
        session.clear()
        conn.close()
        flash('Sesiune invalidă sau expirată. Te rugăm să te reautentifici.', 'error')
        return redirect(url_for('login'))

    # Inițializăm variabilele
    tickets = []
    audit_logs = []

    # LOGICA DE AUTORIZARE (RBAC) 
    if user['role'] == 'MANAGER':
        # Managerul vede TOT 
        tickets = conn.execute('''
            SELECT tickets.*, users.email as owner_email 
            FROM tickets 
            LEFT JOIN users ON tickets.owner_id = users.id
        ''').fetchall()
        
        # Managerul vede audit logs
        audit_logs = conn.execute('''
            SELECT audit_logs.*, users.email 
            FROM audit_logs 
            LEFT JOIN users ON audit_logs.user_id = users.id 
            ORDER BY timestamp DESC LIMIT 20
        ''').fetchall()
    else:
        # Analyst-ul (sau user normal) vede DOAR tichetele lui 
        tickets = conn.execute('SELECT * FROM tickets WHERE owner_id = ?', (user_id,)).fetchall()

    conn.close()
    return render_template('dashboard.html', user=user, tickets=tickets, logs=audit_logs)

# Rută exclusivă pentru Manageri
@app.route('/change_status/<int:ticket_id>', methods=['POST'])
def change_status(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    # CONTROL DE ACCES: Verificăm strict dacă este Manager 
    if not user or user['role'] != 'MANAGER':
        conn.close()
        log_audit(session['user_id'], f"Tentativă neautorizată de schimbare status tichet {ticket_id}", request.remote_addr)
        flash('Eroare: Nu ai permisiunea de a schimba statusul!', 'error')
        return redirect(url_for('dashboard'))

    new_status = request.form['status']
    conn.execute('UPDATE tickets SET status = ? WHERE id = ?', (new_status, ticket_id))
    conn.commit()
    conn.close()

    log_audit(session['user_id'], f"Status schimbat în {new_status} pt tichetul {ticket_id}", request.remote_addr)
    flash('Status actualizat cu succes.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    # SECURE: Verificăm sesiunea pe server, nu în cookie-ul clientului
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Folosim .strip() pentru a elimina spațiile goale introduse accidental (sau malițios)
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        severity = request.form.get('severity', 'LOW')

        # SECURE: Validare pe server (Input Validation). 
        # Niciodată nu avem încredere doar în "required" din HTML.
        if not title or not description:
            flash('Titlul și descrierea sunt obligatorii!', 'error')
            return redirect(url_for('create_ticket'))

        # SECURE: Whitelisting pentru severitate (acceptăm doar valorile definite de noi)
        if severity not in ['LOW', 'MED', 'HIGH']:
            severity = 'LOW'

        conn = get_db_connection()
        # SECURE: Query parametrizat (previne SQL Injection).
        # owner_id este luat din sesiune (user_id), nu din formular, prevenind IDOR.
        cursor = conn.execute(
            'INSERT INTO tickets (title, description, severity, owner_id, status) VALUES (?, ?, ?, ?, ?)',
            (title, description, severity, user_id, 'OPEN')
        )
        ticket_id = cursor.lastrowid # Preluăm ID-ul noului tichet pentru audit
        conn.commit()
        conn.close()

        # SECURE: Trasabilitate. Jurnalizăm acțiunea.
        log_audit(
    user_id, 
    f"A creat tichetul #{ticket_id}", 
    "ticket",          # Parametrul 'resource' 
    str(ticket_id),    # Parametrul 'resource_id' 
    request.remote_addr # Parametrul 'ip_address' 
)

        flash('Tichetul a fost înregistrat cu succes în sistemul securizat.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_ticket.html')

# --- UPDATE: Editare Tichet ---
@app.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def edit_ticket(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Verificăm dacă tichetul există și aparține utilizatorului (Prevenire IDOR)
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ? AND owner_id = ?', (ticket_id, user_id)).fetchone()
    
    if not ticket:
        conn.close()
        flash("Tichetul nu a fost găsit sau nu aveți permisiunea de a-l edita.", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title').strip()
        description = request.form.get('description').strip()
        
        conn.execute('UPDATE tickets SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                     (title, description, ticket_id))
        conn.commit()
        conn.close()
        
        log_audit(user_id, f"A editat tichetul #{ticket_id}", "ticket", str(ticket_id), request.remote_addr)
        flash("Tichetul a fost actualizat!", "success")
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_ticket.html', ticket=ticket)

# --- DELETE: Ștergere Tichet ---
@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Prevenire IDOR: Doar owner-ul poate șterge tichetul
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ? AND owner_id = ?', (ticket_id, user_id)).fetchone()
    
    if ticket:
        conn.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        conn.commit()
        log_audit(user_id, f"A șters tichetul #{ticket_id}", "ticket", str(ticket_id), request.remote_addr)
        flash("Tichetul a fost șters definitiv.", "success")
    else:
        flash("Eroare: Nu poți șterge acest tichet.", "error")
        
    conn.close()
    return redirect(url_for('dashboard'))
@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    query = request.args.get('q', '').strip()
    user_id = session['user_id']
    
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # SECURE: Query Parametrizat (Prevenire SQL Injection)
    # Folosim LIKE cu parametrii `?` protejați
    if user['role'] == 'MANAGER':
        # Managerul caută în toate tichetele
        tickets = conn.execute(
            'SELECT * FROM tickets WHERE title LIKE ? OR description LIKE ?', 
            (f'%{query}%', f'%{query}%')
        ).fetchall()
    else:
        # Analystul caută doar în ale lui (Prevenire IDOR la search)
        tickets = conn.execute(
            'SELECT * FROM tickets WHERE owner_id = ? AND (title LIKE ? OR description LIKE ?)', 
            (user_id, f'%{query}%', f'%{query}%')
        ).fetchall()

    # Jurnalizăm căutarea
    log_audit(user_id, f"Cautare query: {query}", "ticket", None, request.remote_addr)
    conn.close()

    return render_template('dashboard.html', user=user, tickets=tickets, search_query=query)
