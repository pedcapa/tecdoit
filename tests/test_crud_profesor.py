import pytest
from sqlalchemy.orm import Session

from app import schemas
from app.crud import profesor as crud_profesor


def test_create_and_get_profesor(db_session: Session):
    # 1) Crear
    payload = schemas.ProfesorCreate(
        nombre="Test",
        apellido="User",
        correo="testuser@example.com",
        pwd="password123",
        campus="CampusX",
        titulo="Dr.",
        cargo="Tester",
        bio="Bio de prueba",
        avatar_url="http://example.com/avatar.png"
    )
    prof = crud_profesor.create_profesor(db_session, payload)
    assert prof.id_profesor is not None
    assert prof.nombre == "Test"
    assert prof.correo == "testuser@example.com"

    # 2) Get by email
    fetched = crud_profesor.get_by_email(db_session, payload.correo)
    assert fetched is not None
    assert fetched.id_profesor == prof.id_profesor

    # 3) List
    all_profs = crud_profesor.list_profesores(db_session, skip=0, limit=10)
    assert any(p.id_profesor == prof.id_profesor for p in all_profs)

    # 4) Patch
    updated = crud_profesor.patch_profesor(
        db_session, prof.id_profesor, {"titulo": "Prof. C."}
    )
    assert updated.titulo == "Prof. C."
