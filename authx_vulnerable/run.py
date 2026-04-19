# run.py
from app import app

if __name__ == '__main__':
    # Rulăm aplicația în modul debug pentru a vedea erorile (vulnerabilitate de tip information disclosure!)
    app.run(debug=True, port=5000)