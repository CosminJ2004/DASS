# app/__init__.py
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import os
from datetime import timedelta

app = Flask(__name__)

# SECURE: Cheie generată aleatoriu la fiecare pornire (pentru proiect e ok, în producție folosești un .env)
app.secret_key = os.urandom(32)

# SECURE: Configurare flag-uri pentru Cookie-uri (Fix 4.5)
app.config['SESSION_COOKIE_HTTPONLY'] = True # Previne accesul XSS la cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Previne atacurile CSRF
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) # Expirare sesiune

DATABASE = 'secure_app.db'

# SECURE: Rate Limiter pentru a preveni atacurile Brute Force și DoS
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

# Helper pentru logging de securitate
def log_audit(user_id, action, ip_address):
    conn = get_db_connection()
    conn.execute('INSERT INTO audit_logs (user_id, action, ip_address) VALUES (?, ?, ?)',
                 (user_id, action, ip_address))
    conn.commit()
    conn.close()

from app import routes_auth, routes_app