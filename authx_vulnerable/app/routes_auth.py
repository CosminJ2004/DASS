# app/routes_auth.py
from flask import render_template, request, redirect, url_for, flash, make_response
from app import app, get_db_connection
import base64

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # VULNERABILITATE: Password Policy slab (acceptă parole scurte/triviale)
        if not email or not password:
            flash('Toate câmpurile sunt obligatorii.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        try:
            # VULNERABILITATE: Stocare nesigură a parolelor (stocate în clar) 
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

        if user is None:
            flash('Utilizatorul nu există în baza de date!')
            return redirect(url_for('login'))
        
        if user['password'] != password:
            flash('Parola este greșită!')
            return redirect(url_for('login'))

        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('user_id', str(user['id']))
        
        # VULNERABILITATE NOUĂ: Salvăm rolul direct în cookie! 
        # Serverul va avea încredere oarbă în acest cookie ulterior.
        response.set_cookie('role', user['role']) 
        
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
    # Dacă utilizatorul a completat formularul și a apăsat butonul de trimitere
    if request.method == 'POST':
        email = request.form['email']
        
        # Generăm un token complet previzibil (Base64 al email-ului)
        token = base64.b64encode(email.encode('utf-8')).decode('utf-8')
        
        # Afișăm link-ul direct pe ecran (simulăm trimiterea email-ului)
        flash(f"Link resetare: /reset?token={token}")
        return redirect(url_for('login'))

    # Dacă utilizatorul doar a accesat pagina (request de tip GET)
    return render_template('forgot.html')
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    token = request.args.get('token')
    # Decodăm email-ul direct din token fără nicio verificare de securitate
    email = base64.b64decode(token).decode()
    
    if request.method == 'POST':
        new_password = request.form['password']
        conn = get_db_connection()
        # Actualizăm parola direct (Vulnerabilitate: link-ul nu expiră niciodată)
        conn.execute('UPDATE users SET password = ? WHERE email = ?', (new_password, email))
        conn.commit()
        conn.close()
        flash("Parola a fost schimbată!")
        return redirect(url_for('login'))
    return render_template('reset.html', token=token)