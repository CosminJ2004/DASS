# app/routes_auth.py
from flask import render_template, request, redirect, url_for, flash, make_response
from app import app, get_db_connection
import base64

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # VULNERABILITATE: Password Policy slab (acceptă parole scurte/triviale) [cite: 11]
        if not email or not password:
            flash('Toate câmpurile sunt obligatorii.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        try:
            # VULNERABILITATE: Stocare nesigură a parolelor (stocate în clar) [cite: 11]
            conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
            flash('Cont creat cu succes! Te poți loga.')
            return redirect(url_for('login'))
        except conn.IntegrityError:
            flash('Emailul există deja.')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        # VULNERABILITATE: User Enumeration (mesaje diferite pentru user greșit vs parolă greșită) [cite: 14]
        if user is None:
            flash('Utilizatorul nu există în baza de date!')
            return redirect(url_for('login'))
        
        if user['password'] != password:
            flash('Parola este greșită!')
            return redirect(url_for('login'))

        # VULNERABILITATE: Gestionare nesigură a sesiunilor [cite: 14]
        # Setăm un cookie simplu cu ID-ul userului, fără HttpOnly, Secure sau expirare
        # Acest lucru permite IDOR (Insecure Direct Object Reference) și Session Hijacking
        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('user_id', str(user['id']))
        return response

    return render_template('login.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    # Ștergem cookie-ul, dar un atacator l-ar putea recrea manual
    response.set_cookie('user_id', '', expires=0)
    return response

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        
        # VULNERABILITATE: Resetare parolă nesigură (Token predictibil) [cite: 14]
        # Generăm un "token" care este doar email-ul codat în Base64
        token_bytes = email.encode('utf-8')
        token_b64 = base64.b64encode(token_bytes).decode('utf-8')
        
        # În realitate am trimite un email. Aici doar îl afișăm (simulare)
        flash(f'Link de resetare (simulat): /reset?token={token_b64}')
        return redirect(url_for('forgot'))

    return render_template('forgot.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    token = request.args.get('token')
    
    if request.method == 'POST':
        new_password = request.form['password']
        # Decodăm token-ul pentru a afla user-ul
        try:
            email_bytes = base64.b64decode(token)
            email = email_bytes.decode('utf-8')
        except:
            flash('Token invalid.')
            return redirect(url_for('login'))

        conn = get_db_connection()
        conn.execute('UPDATE users SET password = ? WHERE email = ?', (new_password, email))
        conn.commit()
        conn.close()

        flash('Parola a fost resetată! Te poți loga.')
        return redirect(url_for('login'))

    return render_template('reset.html', token=token)