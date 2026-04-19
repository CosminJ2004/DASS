# init_db.py
import sqlite3

def init_db():
    connection = sqlite3.connect('secure_app.db')
    cursor = connection.cursor()

    # Tabelul USERS (Securizat cu failed_attempts și locked)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, 
            role TEXT DEFAULT 'USER',
            failed_attempts INTEGER DEFAULT 0,
            locked BOOLEAN DEFAULT 0,
            session_token TEXT, -- COLOANĂ NOUĂ AICI
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabelul TICKETS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            severity TEXT,
            status TEXT DEFAULT 'OPEN',
            owner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')

    # Tabelul AUDIT_LOGS (Esențial pentru trasabilitate)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabel pentru TOKEN-URI DE RESETARE (Fix pentru 4.6)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL
        )
    ''')

    connection.commit()
    connection.close()
    print("[*] Baza de date SECURE_APP.DB a fost inițializată cu succes!")

if __name__ == '__main__':
    init_db()