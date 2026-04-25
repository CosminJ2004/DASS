import requests
import time

BASE_URL = "http://127.0.0.1:5000"
TEST_EMAIL = "jalba.cosmin@email.com"  # Folosește un email valid din baza ta de date
TEST_PASS = "Cosmin2!"      # Folosește parola validă a acelui email

def test_access_control():
    print("\n[*] Testare Broken Access Control (Rute protejate)...")
    # Încercăm să accesăm dashboard-ul fără a fi logați
    response = requests.get(f"{BASE_URL}/dashboard", allow_redirects=False)
    # Dacă primim 302 (Found) înseamnă că serverul ne trimite înapoi la login
    if response.status_code in [301, 302]:
        print("[SUCCESS] Accesul neautorizat la '/dashboard' a fost blocat (Redirecționare activă).")
    else:
        print(f"[FAIL] Acces permis fără autentificare! Status: {response.status_code}")

def test_user_enumeration():
    print("\n[*] Testare User Enumeration (Mesaje Generice)...")
    res1 = requests.post(f"{BASE_URL}/login", data={'email': 'inexistent_complet@test.com', 'password': 'any'})
    res2 = requests.post(f"{BASE_URL}/login", data={'email': TEST_EMAIL, 'password': 'parola_gresita_intentionat'})
    
    if res1.text == res2.text:
        print("[SUCCESS] Mesajele de eroare sunt identice (Prevenire Enumerare confirmata).")
    else:
        print("[FAIL] Serverul scurge informații (mesajele diferă).")


def test_sql_injection():
    print("\n[*] Testare SQL Injection (Căutare Parametrizată)...")
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={'email': TEST_EMAIL, 'password': TEST_PASS})

    payload = "' OR 1=1 --"
    response = session.get(f"{BASE_URL}/search", params={'q': payload})

    # Verificăm ca serverul să nu fi dat un 500 Internal Error din cauza bazei de date corupte
    if response.status_code == 200 and "sqlite3.OperationalError" not in response.text:
        print("[SUCCESS] Interogarea SQLi a fost tratată ca text sigur (Aplicația nu a crăpat).")
    else:
        print("[FAIL] Posibilă vulnerabilitate SQLi detectată!")

def test_xss_protection():
    print("\n[*] Testare Stored XSS (Jinja2 Auto-Escaping)...")
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={'email': TEST_EMAIL, 'password': TEST_PASS})

    payload = "<script>alert('XSS_Test')</script>"
    # Creăm un tichet cu un payload malițios
    session.post(f"{BASE_URL}/create_ticket", data={'title': 'Test Automat XSS', 'description': payload, 'severity': 'LOW'})

    # Accesăm dashboard-ul pentru a vedea cum randează serverul textul
    dash_resp = session.get(f"{BASE_URL}/dashboard")
    
    # Dacă payload-ul este convertit în entități HTML (ex: &lt;script&gt;), XSS este blocat
    if "&lt;script&gt;" in dash_resp.text or payload not in dash_resp.text:
        print("[SUCCESS] Payload-ul malițios a fost neutralizat cu succes (Auto-Escaping activ).")
    else:
        print("[FAIL] Vulnerabilitate XSS! Scriptul a fost introdus ca text brut în pagină.")

def test_rate_limiting():
    print("\n[*] Testare Rate Limiting (Brute Force Protection)...")
    print("    -> [Avertisment] Acest test rulează intenționat la final pentru a nu bloca IP-ul.")
    email = "bruteforce@test.com"
    for i in range(7):
        response = requests.post(f"{BASE_URL}/login", data={'email': email, 'password': 'wrong_password'})
        if response.status_code == 429:
            print(f"[SUCCESS] Serverul a blocat atacul la încercarea {i+1} cu codul HTTP 429 (Too Many Requests).")
            return
        time.sleep(0.2)
    print("[FAIL] Serverul nu a limitat cererile.")

if __name__ == "__main__":
    print("=======================================================")
    print("      Pornire Teste Automate de Securitate AuthX v2    ")
    print("=======================================================")
    try:
        # Testele inofensive primele
        test_access_control()
        test_user_enumeration()
        test_session_cookies()
        test_sql_injection()
        test_xss_protection()
        
        # Testul agresiv ultimul
        test_rate_limiting()
        
        print("\n[+] Toate testele s-au finalizat cu succes!")
    except requests.exceptions.ConnectionError:
        print(f"\n[!] Eroare CRITICĂ: Nu mă pot conecta la {BASE_URL}. Ai pornit serverul Flask?")