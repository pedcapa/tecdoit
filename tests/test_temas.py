"""
tests/test_temas.py
-------------------
CRUD completo de /temas
"""
from app.models import Tema


def test_create_tema(client, token):
    payload = {"nombre": "Trigonometría", "descripcion": "Razones trig."}
    resp = client.post(
        "/temas",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["nombre"] == "Trigonometría"


def test_list_temas(client):
    resp = client.get("/temas")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_patch_tema(client, token, db_session):
    tema = db_session.query(Tema).first()
    resp = client.patch(
        f"/temas/{tema.id_tema}",
        json={"descripcion": "Actualizado"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["descripcion"] == "Actualizado"


def test_delete_tema(client, token, db_session):
    tema = db_session.query(Tema).first()
    resp = client.delete(
        f"/temas/{tema.id_tema}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
