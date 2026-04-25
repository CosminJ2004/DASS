
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

# Definim cheia și datele (fix cum era în cerință)
key = b'o cheie oarecare'
data = b'testtesttesttesttesttesttesttesttesttesttesttest'

# Generăm un IV (Initialization Vector) aleator de 16 octeți
iv = get_random_bytes(AES.block_size)

# Inițializăm cipher-ul în modul CBC, oferindu-i cheia și IV-ul
cipher = AES.new(key, AES.MODE_CBC, iv)

# Adăugăm padding datelor (le completăm ca să fie exact multiplu de 16)
padded_data = pad(data, AES.block_size)

# Criptăm datele finale
ciphertext = cipher.encrypt(padded_data)

# Afișăm rezultatele în format hexazecimal ca să fie mai ușor de citit
print(f"IV: {iv.hex()}")
print(f"Ciphertext: {ciphertext.hex()}")



key = b'o cheie oarecare'
data = b'test' # Date mai mici de 16 octeți

# Inițializăm cipher-ul
cipher = AES.new(key, AES.MODE_ECB)

# Aplicăm padding pe date înainte de criptare
# AES.block_size este constanta pentru 16
padded_data = pad(data, AES.block_size)

# Criptăm datele umplute
ciphertext = cipher.encrypt(padded_data)

print(ciphertext)



from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

key = b'o cheie oarecare'
data = b'testtesttesttesttesttesttesttesttesttesttesttest'

# Generăm un IV aleator de 16 bytes
iv = get_random_bytes(AES.block_size)

# Folosim AES în modul CBC și îi pasăm IV-ul
cipher = AES.new(key, AES.MODE_CBC, iv)

# Padăm datele (este o bună practică chiar dacă pare că se potrivesc, 
# pentru ca decriptarea să șteargă automat padding-ul corect)
padded_data = pad(data, AES.block_size)

# Criptăm
ciphertext = cipher.encrypt(padded_data)

print(f"IV: {iv.hex()}")
print(f"Ciphertext: {ciphertext.hex()}")

# 234 841136 411758 273000 763594 354834 942653 (39 digits) = 14 086963 408384 851001 × 16 670813 262138 239653


p = 14086963408384851001
q = 16670813262138239653
e = 65537
# Calculăm funcția lui Euler (phi)
phi = (p - 1) * (q - 1)
# Calculăm d (inversul modular al lui e modulo phi)
d = pow(e, -1, phi)
print(f"d = {d}") #d = 131139372709478882400526464589358085473