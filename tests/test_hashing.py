import re
import pytest
from app.utils.hashing import get_password_hash, verify_password

@pytest.mark.parametrize("pwd", [
    "abc123", "ContraseñaConÑ!@#", "  espacios  ", "短密码", "😀🔒"
])
def test_hash_and_verify(pwd):
    # Genera hash
    h = get_password_hash(pwd)
    # El hash debe comenzar con el prefijo de bcrypt y coste 12
    assert re.match(r"^\$2b\$12\$", h)
    # Verificar con la contraseña correcta
    assert verify_password(pwd, h)
    # Fallar con otra contraseña
    assert not verify_password(pwd + "x", h)

def test_hash_uniqueness():
    # Dos hashes para la misma pwd deben ser distintos (sal aleatoria)
    h1 = get_password_hash("misuperpwd")
    h2 = get_password_hash("misuperpwd")
    assert h1 != h2
    # Pero ambos deben validar
    assert verify_password("misuperpwd", h1)
    assert verify_password("misuperpwd", h2)
