import pytest
from app import app 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_password_complexity_rejects_short(client):
    print("\n[*] Rulare test: Parolă prea scurtă (vulnerabilă)...")
    response = client.post('/register', data={
        'email': 'hacker@test.com',
        'password': '123'
    }, follow_redirects=True) # <-- AICI E FIX-UL
    
    # Acum va găsi mesajul pentru că a încărcat pagina finală
    assert b'minim 8 caractere' in response.data
    print("[SUCCESS] Serverul a respins corect parola slabă.")

def test_password_complexity_accepts_strong(client):
    print("\n[*] Rulare test: Parolă complexă (conform politicii)...")
    response = client.post('/register', data={
        'email': 'user_legitim2@test.com',
        'password': 'SuperPassword123!'
    }, follow_redirects=True) # <-- Adăugăm și aici pentru siguranță
    
    assert b'minim 8 caractere' not in response.data
    print("[SUCCESS] Serverul a acceptat formatul parolei puternice.")