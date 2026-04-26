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
app.config['SESSION_COOKIE_SECURE'] = True    # Cookie-ul este trimis DOAR prin HTTPS
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

# app/__init__.py
def log_audit(user_id, action, resource, resource_id, ip_address):
    conn = get_db_connection()
    conn.execute('INSERT INTO audit_logs (user_id, action, resource, resource_id, ip_address) VALUES (?, ?, ?, ?, ?)',
                 (user_id, action, resource, resource_id, ip_address))
    conn.commit()
    conn.close()
from app import routes_auth, routes_app

@app.after_request
def add_security_headers(response):
    # Aceasta este o politică CSP restrictivă și sigură
    csp_policy = (
        "default-src 'self'; "      # Permite resurse doar de pe domeniul propriu
        "script-src 'self'; "       # Permite scripturi DOAR din fișierele locale
        "style-src 'self' 'unsafe-inline'; " # Permite CSS propriu și stiluri inline
        "img-src 'self' data:; "    # Permite imagini locale sau de tip data:
        "frame-ancestors 'none';"   # Previne Clickjacking (nu permite afișarea în <iframe>)
    )
    response.headers['Content-Security-Policy'] = csp_policy
    return response