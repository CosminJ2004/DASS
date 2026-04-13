echo === Pornire Setup ===

REM 1. Verificam/Cream venv
IF NOT EXIST "venv\" (
    echo [*] Nu exista venv. Se creeaza...
    python -m venv venv
) ELSE (
    echo [*] venv gasit.
)

REM 2. Activam venv
echo [*] Activare venv...
call venv\Scripts\activate.bat

REM 3. Instalam dependente
echo [*] Instalare dependente din requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 4. Initializam BD
IF NOT EXIST "vulnerable_app.db" (
    echo [*] Creare baza de date...
    python init_db.py
) ELSE (
    echo [*] Baza de date exista deja.
)

REM 5. Pornire app
echo [*] Pornire aplicatie Flask...
python run.py

pause