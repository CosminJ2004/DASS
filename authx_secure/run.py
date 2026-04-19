# run.py
from app import app

if __name__ == '__main__':
    # SECURE: debug=False în producție pentru a preveni Information Disclosure (Stack Traces)
    app.run(debug=False, port=5000)