import pytest
from jose import jwt, JWTError
from app.utils.security import create_access_token
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MIN

@pytest.fixture
def sample_data():
    return {"id_profesor": 7, "rol": "admin"}

def test_create_and_decode_token(sample_data):
    token = create_access_token(sample_data, expires_delta=5)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["id_profesor"] == sample_data["id_profesor"]
    assert payload["rol"] == sample_data["rol"]
    assert isinstance(payload.get("exp"), int)

def test_token_with_default_expiration(sample_data):
    token   = create_access_token(sample_data)  # usa el default
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    now     = int(__import__("time").time())
    delta   = payload["exp"] - now
    # permits ±5s de desfase
    assert 0 < delta <= (ACCESS_TOKEN_EXPIRE_MIN * 60) + 5

def test_invalid_signature(sample_data):
    token = create_access_token(sample_data, expires_delta=5)
    # modificar un carácter del token
    bad_token = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(JWTError):
        jwt.decode(bad_token, SECRET_KEY, algorithms=[ALGORITHM])

def test_exp_claim_always_present(sample_data):
    token   = create_access_token(sample_data, expires_delta=None)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload
