"""
tests/test_auth.py
------------------
Pruebas de los endpoints de autenticación.
"""
import uuid
import pytest
from app.utils.hashing import verify_password


def test_login_success(client, test_user):
    resp = client.post(
        "/auth/login",
        data={"username": test_user.correo, "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and data["token_type"] == "bearer"


def test_login_fail_wrong_pwd(client, test_user):
    resp = client.post(
        "/auth/login",
        data={"username": test_user.correo, "password": "bad"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 400


@pytest.mark.usefixtures("db_session")
def test_register_profesor(client, token, db_session):
    """Solo admin puede registrar."""
    correo_nuevo = f"nuevo-{uuid.uuid4().hex}@test.mx"
    payload = {
        "nombre": "Nuevo",
        "apellido": "Profesor",
        "correo": correo_nuevo,
        "pwd": "temporal1",
        "rol": "autor",
    }
    resp = client.post(
        "/auth/register",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["correo"] == correo_nuevo
    # Verifica que la contraseña quedó hasheada en BD
    from app.models import Profesor
    
    prof = db_session.get(Profesor, data["id_profesor"])
    assert verify_password("temporal1", prof.pwd)
