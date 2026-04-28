# AuthX - Sistem de Ticketing Securizat (Proiect DASS)

**Student:** Jalba Cosmin 
**Grupa:** 333

## 📌 Descrierea Proiectului
AuthX este o platformă de suport tehnic (Ticketing System) dezvoltată pentru gestionarea resurselor corporative sensibile. Proiectul urmărește metodologia **"Build, Hack, Secure"**, demonstrând tranziția de la o aplicație vulnerabilă (v1) la un sistem robust, securizat prin principii de *security-by-design* (v2).

## 🌿 Structura Repository-ului (GitHub)
Proiectul utilizează ramuri (branches) pentru a evidenția etapele auditului de securitate:
* **`main`**: Conține versiunea finală, securizată și testată a aplicației (v2 mergeuită).
* **`v1-vulnerable`**: Versiunea MVP ce conține deficiențe majore conform OWASP (parole în clar, SQL Injection, XSS).
* **`v2-secure`**: Versiunea refactorizată în care au fost implementate toate remediile de securitate.

## 🛠️ Arhitectura Tehnologică
* **Backend:** Python 3 utilizând framework-ul Flask.
* **Frontend:** Template-uri Jinja2 pentru randare HTML dinamică.
* **Bază de Date:** SQLite pentru stocare persistentă.
* **Mediul de Execuție:** Mașină Virtuală (VM) Ubuntu Linux.
* **Dependințe Securitate:** `bcrypt` (hashing) și `Flask-Limiter` (rate limiting).

## 🔍 Analiza Securității: v1 vs v2

| Funcționalitate | Status v1 (Vulnerabil) | Remediere v2 (Securizat) |
| :--- | :--- | :--- |
| **Validare Parolă** | Fără restricții (acceptă „123”)  | Minim 8 caractere + cifră  |
| **Stocare Parole** | Text în clar (Plain text)  | Hash modern cu Bcrypt + Salt  |
| **Mesaje Login** | Eroare diferențiată (Enumeration)  | Mesaj generic: „Email sau parola gresita”  |
| **Protecție Brute Force**| Inexistentă (cereri nelimitate)  | Rate Limiting (5 încercări/minut)  |
| **Interogări SQL** | Concatenare (Vulnerabil SQLi) | Interogări parametrizate  |
| **Afișare Date** | Randare directă (Vulnerabil XSS)  | Auto-escaping via Jinja2 |
| **Cookie-uri** | Fără flag-uri de securitate  | HttpOnly, Secure, SameSite='Strict' |
| **Control Acces** | Lipsă verificare (IDOR)  | Validare server-side a `owner_id`  |

