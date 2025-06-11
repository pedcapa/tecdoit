import pytest
from app.utils.hashing import get_password_hash, verify_password

def test_hash_and_verify_password():
    password = "SuperSecreto123!"
    # Genera un hash distinto al texto plano
    hashed = get_password_hash(password)
    assert hashed != password
    # Verificación correcta
    assert verify_password(password, hashed) is True
    # Verificación incorrecta
    assert verify_password("OtraContraseña", hashed) is False

@pytest.mark.parametrize("pwd", ["abc", "123456", "!@#$$%^"])
def test_hash_uniqueness(pwd):
    # Cada llamada a gensalt produce un hash distinto
    h1 = get_password_hash(pwd)
    h2 = get_password_hash(pwd)
    assert h1 != h2
    assert verify_password(pwd, h1)
    assert verify_password(pwd, h2)
