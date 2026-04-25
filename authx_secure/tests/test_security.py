import pytest
from app.routes_auth import validate_password # presupunând că ai funcția extrasă

def test_password_complexity_rejects_short():
    # Testăm dacă v2 respinge corect o parolă scurtă
    assert validate_password("123") is False

def test_password_complexity_accepts_strong():
    # Testăm dacă acceptă o parolă conform politicii
    assert validate_password("ParolaSecura123!") is True