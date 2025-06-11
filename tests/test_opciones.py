# tests/test_opciones.py
"""
Pruebas para el router de Opciones:
- POST /preguntas/{pid}/opciones/
- PATCH /preguntas/{pid}/opciones/{id_opcion}
- DELETE /preguntas/{pid}/opciones/{id_opcion}
"""
import uuid
import pytest
from app.models import Pregunta, Opcion, Profesor
from app.utils.hashing import get_password_hash


def _create_question(db_session, author_id):
    """Helper: crea una pregunta mínima para vincular opciones."""
    q = Pregunta(
        enunciado="¿Test?",
        tipo="abc",
        id_isla=1,
        dificultad=1,
        randomizar=False,
        id_profesor=author_id
    )
    db_session.add(q)
    db_session.flush()
    return q


def test_add_opcion_success(client, token, db_session, test_user):
    # Prepara: crea pregunta
    q = _create_question(db_session, test_user.id_profesor)
    db_session.commit()

    payload = {"texto": "Respuesta", "es_correcta": True}
    resp = client.post(
        f"/preguntas/{q.id_pregunta}/opciones/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["texto"] == "Respuesta"
    assert data["es_correcta"] is True

    # Verificar en BD
    opt = db_session.get(Opcion, data["id_opcion"])
    assert opt is not None
    assert opt.texto == "Respuesta"


def test_patch_opcion_success(client, token, db_session, test_user):
    # Prepara: crea pregunta + opción
    q = _create_question(db_session, test_user.id_profesor)
    db_session.flush()
    opt = Opcion(
        id_pregunta=q.id_pregunta,
        texto="Antes",
        es_correcta=False,
        id_profesor=test_user.id_profesor
    )
    db_session.add(opt)
    db_session.commit()

    payload = {"texto": "Después", "es_correcta": True}
    resp = client.patch(
        f"/preguntas/{q.id_pregunta}/opciones/{opt.id_opcion}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["texto"] == "Después"
    assert data["es_correcta"] is True

    # Verificar en BD
    updated = db_session.get(Opcion, opt.id_opcion)
    assert updated.texto == "Después"
    assert updated.es_correcta is True


def test_patch_opcion_not_found(client, token, db_session):
    # Patch a opción inexistente
    resp = client.patch(
        "/preguntas/1/opciones/9999",
        json={"texto": "X", "es_correcta": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


def test_patch_opcion_not_owner(client, token, db_session, test_user):
    # Crea otro profesor en BD para simular “no propietario”
    other = Profesor(
        nombre="Bob",
        apellido="NotOwner",
        correo=f"bob-{uuid.uuid4().hex}@test.mx",
        pwd=get_password_hash("irrelevant"),
        rol="autor",
        activo=True,
    )
    db_session.add(other)
    db_session.flush()

    # Crea pregunta y opción asignadas a este otro profesor
    q = _create_question(db_session, other.id_profesor)
    db_session.flush()
    opt = Opcion(
        id_pregunta=q.id_pregunta,
        texto="Otro",
        es_correcta=False,
        id_profesor=other.id_profesor
    )
    db_session.add(opt)
    db_session.commit()

    resp = client.patch(
        f"/preguntas/{q.id_pregunta}/opciones/{opt.id_opcion}",
        json={"texto": "X", "es_correcta": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


def test_delete_opcion_success(client, token, db_session, test_user):
    # Prepara: crea pregunta + opción
    q = _create_question(db_session, test_user.id_profesor)
    db_session.flush()
    opt = Opcion(
        id_pregunta=q.id_pregunta,
        texto="A borrar",
        es_correcta=False,
        id_profesor=test_user.id_profesor
    )
    db_session.add(opt)
    db_session.commit()

    resp = client.delete(
        f"/preguntas/{q.id_pregunta}/opciones/{opt.id_opcion}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 204

    # Verificar en BD
    assert db_session.get(Opcion, opt.id_opcion) is None


def test_delete_opcion_nonexistent(client, token):
    # Borrar id que no existe → 204 igualmente
    resp = client.delete(
        "/preguntas/1/opciones/9999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 204
