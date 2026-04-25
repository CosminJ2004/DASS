import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_rate_limiting():
    print("[*] Testare Rate Limiting (Brute Force Protection)...")
    email = "test@example.com"
    for i in range(7): # Încercăm de 7 ori (limita e 5)
        response = requests.post(f"{BASE_URL}/login", data={'email': email, 'password': 'wrong_password'})
        if response.status_code == 429:
            print(f"[SUCCESS] Serverul a blocat atacul la încercarea {i+1} cu codul 429.")
            return
    print("[FAIL] Serverul nu a limitat cererile.")

def test_user_enumeration():
    print("\n[*] Testare User Enumeration (Generic Messages)...")
    # Mesaj pentru user inexistent
    res1 = requests.post(f"{BASE_URL}/login", data={'email': 'nonexistent@test.com', 'password': 'any'})
    # Mesaj pentru user existent, parola greșită
    res2 = requests.post(f"{BASE_URL}/login", data={'email': 'admin@authx.ro', 'password': 'wrong'})
    
    if res1.text == res2.text:
        print("[SUCCESS] Mesajele de eroare sunt identice (Prevenire Enumerare).")
    else:
        print("[FAIL] Serverul scurge informații prin mesaje diferite.")

def test_session_cookies():
    print("\n[*] Testare Security Headers (HttpOnly)...")
    # Ne logăm pentru a primi un cookie
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={'email': 'admin@authx.ro', 'password': 'password123'})
    
    cookies = session.cookies
    for cookie in cookies:
        if cookie.has_nonstandard_attr('HttpOnly') or cookie.rest.get('HttpOnly'):
            print(f"[SUCCESS] Cookie-ul '{cookie.name}' are flag-ul HttpOnly setat.")
        else:
            print(f"[FAIL] Cookie-ul '{cookie.name}' NU este securizat!")

if __name__ == "__main__":
    print("=== Pornire Teste Automate de Securitate AuthX v2 ===")
    try:
        test_rate_limiting()
        test_user_enumeration()
        test_session_cookies()
    except Exception as e:
        print(f"[!] Eroare: Asigură-te că serverul Flask rulează la {BASE_URL}")