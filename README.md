# AuthX - Sistem de Ticketing Securizat (Proiect DASS)

[cite_start]**Student:** Jalba Cosmin [cite: 2]  
[cite_start]**Grupa:** 333 [cite: 2]

## 📌 Descrierea Proiectului
[cite_start]AuthX este o platformă de suport tehnic (Ticketing System) dezvoltată pentru gestionarea resurselor corporative sensibile[cite: 5, 7]. [cite_start]Proiectul urmărește metodologia **"Build, Hack, Secure"**, demonstrând tranziția de la o aplicație vulnerabilă (v1) la un sistem robust, securizat prin principii de *security-by-design* (v2)[cite: 10, 12, 13].

## 🌿 Structura Repository-ului (GitHub)
Proiectul utilizează ramuri (branches) pentru a evidenția etapele auditului de securitate:
* [cite_start]**`main`**: Conține versiunea finală, securizată și testată a aplicației (v2 mergeuită)[cite: 306].
* [cite_start]**`v1-vulnerable`**: Versiunea MVP ce conține deficiențe majore conform OWASP (parole în clar, SQL Injection, XSS)[cite: 6, 74].
* [cite_start]**`v2-secure`**: Versiunea refactorizată în care au fost implementate toate remediile de securitate[cite: 203, 204].

## 🛠️ Arhitectura Tehnologică
* [cite_start]**Backend:** Python 3 utilizând framework-ul Flask[cite: 17, 36, 38].
* [cite_start]**Frontend:** Template-uri Jinja2 pentru randare HTML dinamică[cite: 16].
* [cite_start]**Bază de Date:** SQLite pentru stocare persistentă[cite: 18, 33].
* [cite_start]**Mediul de Execuție:** Mașină Virtuală (VM) Ubuntu Linux[cite: 19, 30].
* [cite_start]**Dependințe Securitate:** `bcrypt` (hashing) și `Flask-Limiter` (rate limiting)[cite: 40, 41].

## 🔍 Analiza Securității: v1 vs v2

| Funcționalitate | Status v1 (Vulnerabil) | Remediere v2 (Securizat) |
| :--- | :--- | :--- |
| **Validare Parolă** | [cite_start]Fără restricții (acceptă „123”) [cite: 49, 65] | [cite_start]Minim 8 caractere + cifră [cite: 65, 209] |
| **Stocare Parole** | [cite_start]Text în clar (Plain text) [cite: 52, 83] | [cite_start]Hash modern cu Bcrypt + Salt [cite: 65, 208] |
| **Mesaje Login** | [cite_start]Eroare diferențiată (Enumeration) [cite: 57, 93] | [cite_start]Mesaj generic: „Email sau parola gresita” [cite: 221] |
| **Protecție Brute Force**| [cite_start]Inexistentă (cereri nelimitate) [cite: 88, 89] | [cite_start]Rate Limiting (5 încercări/minut) [cite: 217] |
| **Interogări SQL** | [cite_start]Concatenare (Vulnerabil SQLi) [cite: 111] | [cite_start]Interogări parametrizate [cite: 230, 232] |
| **Afișare Date** | [cite_start]Randare directă (Vulnerabil XSS) [cite: 112] | [cite_start]Auto-escaping via Jinja2 [cite: 231, 275] |
| **Cookie-uri** | [cite_start]Fără flag-uri de securitate [cite: 60, 99] | [cite_start]HttpOnly, Secure, SameSite='Strict' [cite: 102, 225] |
| **Control Acces** | [cite_start]Lipsă verificare (IDOR) [cite: 155, 156] | [cite_start]Validare server-side a `owner_id` [cite: 226, 227] |

