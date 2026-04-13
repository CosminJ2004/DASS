# init_db.py
import sqlite3

def init_db():
    connection = sqlite3.connect('vulnerable_app.db')
    cursor = connection.cursor()

    # 1. Tabelul USERS [cite: 25, 26]
    # Vulnerabilitate: 'password' va stoca parola în clar (sau un hash slab mai târziu), nu un hash modern.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, 
            role TEXT DEFAULT 'USER',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            locked BOOLEAN DEFAULT 0
        )
    ''')

    # 2. Tabelul TICKETS [cite: 27, 28]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            severity TEXT,
            status TEXT DEFAULT 'OPEN',
            owner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')

    # 3. Tabelul AUDIT_LOGS [cite: 32, 33]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            resource TEXT,
            resource_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    connection.commit()
    connection.close()
    print("Baza de date vulnerabilă a fost inițializată cu succes!")

if __name__ == '__main__':
    init_db()