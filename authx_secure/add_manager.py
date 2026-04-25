import sqlite3
import bcrypt

def add_manager(email, password):
    conn = sqlite3.connect('secure_app.db')
    cursor = conn.cursor()

    # Generăm hash-ul folosind Bcrypt (exact ca în routes_auth.py)
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    try:
        # Inserăm managerul cu toate câmpurile necesare pentru v2
        cursor.execute('''
            INSERT INTO users (email, password_hash, role, locked, failed_attempts)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, password_hash, 'MANAGER', 0, 0))
        
        conn.commit()
        print(f"[SUCCESS] Managerul {email} a fost adăugat cu succes!")
    except sqlite3.IntegrityError:
        print(f"[ERROR] Utilizatorul {email} există deja în baza de date.")
    finally:
        conn.close()

if __name__ == "__main__":
    # Poți schimba datele de aici
    add_manager('manager@authx.ro', 'ParolaSigura123!')