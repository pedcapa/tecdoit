"""
tests/test_profesores.py
------------------------
/profesores/me  y  endpoints admin.
"""
def test_me_endpoint(client, token):
    resp = client.get(
        "/profesores/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    me = resp.json()
    assert me["correo"].endswith("@test.mx")


def test_list_profesores_admin(client, token):
    resp = client.get(
        "/profesores",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_patch_me_updates_bio(client, token, test_user):
    # Cambiamos solo el campo 'bio' de nuestro perfil
    new_bio = "Entusiasta de las pruebas"

    payload = {
        "nombre": test_user.nombre,
        "apellido": test_user.apellido,
        "correo": test_user.correo,
        "campus": test_user.campus,
        "titulo": test_user.titulo,
        "cargo": test_user.cargo,
        "bio": new_bio,
        "avatar_url": test_user.avatar_url,
    }

    resp = client.patch(
        "/profesores/me",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["bio"] == new_bio

def test_get_prof_by_id_admin(client, token, test_user):
    # Admin puede ver cualquier profesor por ID
    resp = client.get(
        f"/profesores/{test_user.id_profesor}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id_profesor"] == test_user.id_profesor
    assert data["correo"] == test_user.correo

def test_patch_prof_by_admin(client, token, db_session, test_user):
    # Admin desactiva a test_user
    resp = client.patch(
        f"/profesores/{test_user.id_profesor}",
        json={"activo": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["activo"] is False

    # Verificar en BD
    from app.models import Profesor
    prof = db_session.get(Profesor, test_user.id_profesor)
    assert prof.activo is False
