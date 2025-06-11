import pytest
from jose import jwt
from app.config import SECRET_KEY, ALGORITHM
from app.utils.security import create_access_token


# --------------------------------------------------------------------- #
#  get_current_user
# --------------------------------------------------------------------- #
def test_current_user_ok(client, token, test_user):
    r = client.get("/profesores/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["correo"] == test_user.correo


def test_current_user_missing_token(client):
    r = client.get("/profesores/me")
    assert r.status_code == 401


def test_current_user_bad_token(client):
    fake = create_access_token({"sub": 999})
    r = client.get("/profesores/me", headers={"Authorization": f"Bearer {fake}"})
    assert r.status_code == 401


# --------------------------------------------------------------------- #
#  is_admin
# --------------------------------------------------------------------- #
def test_is_admin_ok(client, token):
    r = client.get("/temas", headers={"Authorization": f"Bearer {token}"})
    # /temas es público GET, verificaremos un endpoint admin-only:
    r2 = client.post("/temas", json={"nombre": "Demo"}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code != 403


def test_is_admin_forbidden(client, db_session, test_user):
    # Cambiar rol a autor
    test_user.rol = "autor"; db_session.commit()
    tok = create_access_token({"id_profesor": test_user.id_profesor, "rol": "autor"})
    r = client.post("/temas", json={"nombre": "Demo"},
                    headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 403
