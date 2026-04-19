# app/routes_auth.py
from flask import render_template, request, redirect, url_for, flash, session
from app import app, get_db_connection, limiter, log_audit
import bcrypt
import secrets
from datetime import datetime, timedelta

# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fix 4.1: Password Policy
        if len(password) < 8 or not any(char.isdigit() for char in password):
            flash('Parola trebuie să aibă minim 8 caractere și cel puțin o cifră.', 'error')
            return redirect(url_for('register'))

        # Fix 4.2: Stocare sigură cu Bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
            conn.commit()
            # UPDATED: log_audit cu 5 parametri
            log_audit(None, f"Register succes pentru {email}", "auth", None, request.remote_addr)
            flash('Cont creat cu succes!', 'success')
            return redirect(url_for('login'))
        except conn.IntegrityError:
            # Fix 4.4: Nu confirmăm explicit că email-ul există deja (User Enumeration)
            flash('Dacă adresa nu a fost folosită, contul a fost creat.', 'success')
        finally:
            conn.close()

    return render_template('register.html')


# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=['POST']) # Fix 4.3: Rate limiting sever pe ruta de login
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        # Fix 4.4: Mesaj generic de eroare "Invalid credentials"
        generic_error = 'Email sau parolă incorectă.'

        if user is None:
            conn.close()
            # UPDATED: log_audit cu 5 parametri
            log_audit(None, f"Login eșuat (user inexistent) pt {email}", "auth", None, request.remote_addr)
            flash(generic_error, 'error')
            return redirect(url_for('login'))

        # Fix 4.3: Verificăm dacă contul este blocat
        if user['locked']:
            conn.close()
            # UPDATED: log_audit cu 5 parametri
            log_audit(user['id'], "Login încercat pe cont blocat", "auth", None, request.remote_addr)
            flash('Contul este temporar blocat din cauza prea multor încercări eșuate.', 'error')
            return redirect(url_for('login'))

        # Fix 4.2 & 4.4: Verificăm hash-ul
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Incrementăm failed_attempts
            new_attempts = user['failed_attempts'] + 1
            if new_attempts >= 5:
                conn.execute('UPDATE users SET locked = 1, failed_attempts = ? WHERE id = ?', (new_attempts, user['id']))
                # UPDATED: log_audit cu 5 parametri
                log_audit(user['id'], "CONT BLOCAT - Brute force detectat", "auth", None, request.remote_addr)
            else:
                conn.execute('UPDATE users SET failed_attempts = ? WHERE id = ?', (new_attempts, user['id']))
            conn.commit()
            conn.close()
            
            flash(generic_error, 'error')
            return redirect(url_for('login'))

        # Generăm un identificator unic de sesiune
        session_token = secrets.token_hex(16)
        
        # Îl salvăm în Baza de Date
        conn.execute('UPDATE users SET failed_attempts = 0, session_token = ? WHERE id = ?', 
                     (session_token, user['id']))
        conn.commit()
        conn.close()

        session.clear() 
        session.permanent = True
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['session_token'] = session_token # Îl punem și în cookie-ul criptat
        
        # UPDATED: log_audit cu 5 parametri
        log_audit(user['id'], "Login cu succes", "auth", None, request.remote_addr)
        return redirect(url_for('dashboard'))

    return render_template('login.html')


# --- LOGOUT ---
@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        # ȘTERGEM token-ul din baza de date (Invalidare reală pe server!)
        conn = get_db_connection()
        conn.execute('UPDATE users SET session_token = NULL WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        # UPDATED: log_audit cu 5 parametri
        log_audit(user_id, "Logout", "auth", None, request.remote_addr)
        
    session.clear()
    flash('Te-ai delogat în siguranță.', 'success')
    return redirect(url_for('login'))

# --- FORGOT PASSWORD ---
@app.route('/forgot', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=['POST']) # Previne spam-ul de email-uri
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        # Fix 4.4: Prevenire enumerare. Oferim același răspuns indiferent dacă userul există sau nu.
        flash('Dacă adresa există, un link a fost trimis.', 'info')

        if user:
            # Fix 4.6: Token puternic, aleatoriu și one-time
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(minutes=15)
            
            conn.execute('INSERT INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)',
                         (email, token, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            
            # Aici în mod normal trimiți email-ul. Noi doar îl printăm în terminal.
            print(f"\n[SECURE SYSTEM] Link resetare pentru {email}: /reset?token={token}\n")
            # UPDATED: log_audit cu 5 parametri
            log_audit(user['id'], "Cerere resetare parolă", "auth", None, request.remote_addr)

        conn.close()
        return redirect(url_for('login'))

    return render_template('forgot.html')


# --- RESET PASSWORD ---
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    token = request.args.get('token')
    
    if not token:
        flash('Token lipsă.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    reset_entry = conn.execute('SELECT * FROM password_resets WHERE token = ?', (token,)).fetchone()

    # Verificăm dacă tokenul există și nu a expirat
    if not reset_entry:
        conn.close()
        flash('Token invalid sau deja folosit.', 'error')
        return redirect(url_for('login'))
        
    expires_at = datetime.strptime(reset_entry['expires_at'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() > expires_at:
        conn.execute('DELETE FROM password_resets WHERE id = ?', (reset_entry['id'],))
        conn.commit()
        conn.close()
        flash('Acest link a expirat.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['password']
        
        if len(new_password) < 8 or not any(char.isdigit() for char in new_password):
            flash('Noua parolă trebuie să aibă minim 8 caractere și o cifră.', 'error')
            return redirect(url_for('reset', token=token))

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

        # Actualizăm parola, deblocăm contul dacă era blocat
        conn.execute('UPDATE users SET password_hash = ?, locked = 0, failed_attempts = 0 WHERE email = ?', 
                     (password_hash, reset_entry['email']))
                     
        # Fix 4.6: ȘTERGEM token-ul după utilizare pentru a preveni reutilizarea
        conn.execute('DELETE FROM password_resets WHERE token = ?', (token,))
        conn.commit()
        conn.close()

        flash('Parola a fost resetată cu succes!', 'success')
        return redirect(url_for('login'))

    return render_template('reset.html', token=token)