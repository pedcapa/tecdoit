import pytest
from app.utils.hashing import verify_password

def test_change_password_success(client, token, db_session, test_user):
    resp = client.post(
        "/auth/change-password",
        json={"old_password":"secret","new_password":"otroSecret"},
        headers={"Authorization":f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["msg"] == "Contraseña actualizada exitosamente"

    # Verifica en BD
    from app.models import Profesor
    user = db_session.get(Profesor, test_user.id_profesor)
    assert verify_password("otroSecret", user.pwd)

def test_change_password_wrong_old(client, token):
    resp = client.post(
        "/auth/change-password",
        json={"old_password":"mal","new_password":"noImporta"},
        headers={"Authorization":f"Bearer {token}"}
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "La contraseña actual es incorrecta"
