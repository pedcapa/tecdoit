# tests/test_islas.py
import pytest
from app.models import Isla
from app.utils.security import create_access_token
from app.utils.hashing import get_password_hash

# Fixtures
@pytest.fixture
def admin_token(test_user):
    # test_user de conftest.py ya es admin
    return create_access_token({
        "id_profesor": test_user.id_profesor,
        "rol": test_user.rol,
    })

def test_list_and_get_islas(client, db_session):
    # Seed si no hay islas
    if not db_session.query(Isla).count():
        db_session.add_all([
            Isla(id_isla=1, nombre="Isla Uno"),
            Isla(id_isla=2, nombre="Isla Dos"),
        ])
        db_session.commit()

    # GET /islas
    r = client.get("/islas")
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list) and len(arr) >= 2

    # GET /islas/{id}
    first_id = arr[0]['id_isla']
    r2 = client.get(f"/islas/{first_id}")
    assert r2.status_code == 200
    assert r2.json()["id_isla"] == first_id


def test_create_isla_admin(client, admin_token, db_session):
    payload = {"id_isla": 999, "nombre": "Isla Prueba", "descripcion": "Desc prueba"}

    r = client.post(
        "/islas/",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 201, r.text
    data = r.json()

    # 1) id_isla debe ser un entero > 0 (no forzamos que sea 999)
    assert isinstance(data["id_isla"], int) and data["id_isla"] > 0

    # 2) nombre/descripcion deben coincidir
    assert data["nombre"] == payload["nombre"]
    assert data["descripcion"] == payload["descripcion"]

    # 3) verifica en la BD
    isla_bd = db_session.query(Isla).filter_by(nombre=payload["nombre"]).first()
    assert isla_bd is not None
    assert isla_bd.descripcion == payload["descripcion"]



def test_create_isla_unauthorized(client):
    payload = {"id_isla": 100, "nombre": "Nope", "descripcion": "Desc"}
    # Sin token → 401
    r1 = client.post("/islas/", json=payload)
    assert r1.status_code == 401


def test_create_isla_forbidden(client, db_session):
    # Creamos un autor cualquiera
    from app.models import Profesor
    autor = Profesor(
        nombre="A", apellido="B", correo="autor@test.mx",
        pwd=get_password_hash("x"), rol="autor", activo=True
    )
    db_session.add(autor); db_session.flush()
    from app.utils.security import create_access_token
    t = create_access_token({"id_profesor": autor.id_profesor, "rol": autor.rol})

    payload = {"id_isla": 101, "nombre": "Nope", "descripcion": "Desc"}
    r2 = client.post(
        "/islas/",
        json=payload,
        headers={"Authorization": f"Bearer {t}"}
    )
    assert r2.status_code == 403


def test_update_and_delete_isla_admin(client, admin_token, db_session):
    # 1) Prepara una isla en la BD
    isla = Isla(id_isla=102, nombre="ToUpdate", descripcion="Old")
    db_session.add(isla); db_session.commit()
    iid = isla.id_isla

    # 2) PATCH /islas/{id}
    patch_payload = {
        "id_isla": iid,
        "nombre": "Actualizada",
        "descripcion": "Old"
    }
    r1 = client.patch(
        f"/islas/{iid}",
        json=patch_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r1.status_code == 200, r1.text
    assert r1.json()["nombre"] == "Actualizada"

    # 3) DELETE /islas/{id}
    r2 = client.delete(
        f"/islas/{iid}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r2.status_code == 204

    # 4) Verifica que ya no exista
    assert db_session.get(Isla, iid) is None
