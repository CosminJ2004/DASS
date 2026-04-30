# app/__init__.py
from authx_vulnerable.app import routes_auth
from flask import Flask
import sqlite3

app = Flask(__name__)
# O cheie secretă simplă și hardcodată (Vulnerabilitate!)
app.secret_key = "super_secret_key_123" 

DATABASE = 'vulnerable_app.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    # Returnăm rândurile ca dicționare pentru a fi mai ușor de folosit
    conn.row_factory = sqlite3.Row 
    return conn

# Aici vom importa rutele mai târziu, după ce le creăm
# from app import routes_auth, routes_app
# Importăm rutele după inițializarea aplicației pentru a evita "circular imports"
from app import routes_auth