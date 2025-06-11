import time
from jose import jwt, ExpiredSignatureError
import pytest

from app.utils.security import create_access_token
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MIN

def test_create_access_token_contains_payload_and_exp():
    data = {"id_profesor": 42, "rol": "admin"}
    token = create_access_token(data)
    # Decodificamos el JWT usando las mismas constantes
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # Verificamos que los datos originales estén presentes
    assert decoded["id_profesor"] == 42
    assert decoded["rol"] == "admin"
    # Verificamos que venga el claim 'exp' y que esté en el futuro
    assert "exp" in decoded
    assert decoded["exp"] > time.time()

def test_token_immediately_expired():
    # Crear un token con expiration time en el pasado (expires_delta en minutos)
    token = create_access_token({"foo": "bar"}, expires_delta=-1)
    # Al intentar decodificarlo debe dar ExpiredSignatureError
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
