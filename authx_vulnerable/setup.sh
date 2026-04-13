#!/bin/bash

echo "=== Setup Environment pentru AuthX (v1 - Vulnerabil) ==="

# 1. Verificăm dacă există folderul venv, dacă nu, îl creăm
if [ ! -d "venv" ]; then
    echo "[*] Creare mediu virtual (venv)..."
    python3 -m venv venv
else
    echo "[*] Mediul virtual există deja."
fi

# 2. Activăm mediul virtual
echo "[*] Activare venv..."
source venv/bin/activate

# 3. Instalăm dependențele
echo "[*] Instalare pachete din requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Inițializăm baza de date (dacă nu există deja fișierul .db)
if [ ! -f "vulnerable_app.db" ]; then
    echo "[*] Inițializare bază de date SQLite..."
    python3 init_db.py
fi

# 5. Pornim aplicația
echo "[*] Pornire server Flask..."
python3 run.py