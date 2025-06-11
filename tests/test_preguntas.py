# --------------------------------------------------------------------------
#  NUEVAS PRUEBAS PARA /preguntas
# --------------------------------------------------------------------------
import uuid
import pytest
from app.models import Isla, Tema, Pregunta


def _seed_catalog(db):
    if not db.query(Isla).count():
        db.add(Isla(id_isla=1, nombre="Isla A"))
    if not db.query(Tema).count():
        db.add(Tema(id_tema=1, nombre="Fracciones"))
    db.commit()


@pytest.fixture()
def borrador(client, token, db_session):
    """Crea una pregunta en estado 'borrador' y la devuelve."""
    _seed_catalog(db_session)
    payload = {
        "enunciado": "1+1",
        "tipo": "vf",
        "id_isla": 1,
        "dificultad": 1,
        "randomizar": False,
        "temas": [1],
        "opciones": [
            {"texto": "2", "es_correcta": True},
            {"texto": "3", "es_correcta": False},
        ],
    }
    r = client.post(
        "/preguntas",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    return r.json()           # devuelve dict PreguntaOut


# 1. LISTADO —————————————————————————————————————————
def test_list_preguntas_filtrado(client, token, borrador):
    resp = client.get(
        "/preguntas",
        params={"estado": "borrador", "id_isla": 1, "page": 1, "size": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any(p["id_pregunta"] == borrador["id_pregunta"] for p in data)


# 2. DETALLE —————————————————————————————————————————
def test_get_detalle(client, token, borrador):
    pid = borrador["id_pregunta"]
    r = client.get(
        f"/preguntas/{pid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["enunciado"] == "1+1"


# 3. PATCH (editar) —————————————————————————————
def test_patch_borrador(client, token, borrador):
    pid = borrador["id_pregunta"]
    nuevo = {"enunciado": "1+2", "tipo": "abc", "id_isla": 1,
             "dificultad": 2, "randomizar": True,
             "temas": [1],
             "opciones": [
                 {"texto": "3", "es_correcta": True},
                 {"texto": "4", "es_correcta": False},
             ]}
    r = client.patch(
        f"/preguntas/{pid}",
        json=nuevo,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["enunciado"] == "1+2"
    assert r.json()["randomizar"] is True


# 4. PREVIEW (nuevo esquema) ———————————————————————
def test_preview_endpoint(client):
    # usa el schema PreviewIn → solo necesita {"enunciado": "..."}
    r = client.post("/preguntas/preview-image",
                    json={"enunciado": "a/b"},
                    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"


# 5. BATCH SUBMIT ———————————————————————————————
def test_batch_submit(client, token, db_session, borrador):
    # Creamos otro borrador
    otra = borrador.copy()
    otra_id = borrador["id_pregunta"] + 9999  # aseguramos id distinto
    db_session.add(Pregunta(
        id_pregunta=otra_id,
        enunciado="2+2",
        tipo="vf",
        id_isla=1,
        dificultad=1,
        randomizar=False,
        id_profesor=borrador["id_profesor"],
        estado="borrador",
    )); db_session.commit()

    r = client.post(
        "/preguntas/batch/submit",
        json={"ids": [borrador["id_pregunta"], otra_id]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["enviadas"] == 2


# 6. BATCH DECISION ——————————————————————————————
def test_batch_decision(client, token, db_session):
    # Creamos 2 preguntas 'en revisión' con profesor ficticio
    for i in range(2):
        db_session.add(Pregunta(
            enunciado=f"p{i}",
            tipo="vf",
            id_isla=1,
            dificultad=1,
            randomizar=False,
            id_profesor=1,
            estado="en revisión",
        ))
    db_session.commit()
    ids = [p.id_pregunta for p in db_session.query(Pregunta)
           .filter(Pregunta.estado == "en revisión").all()]

    body = {"ids": ids, "decision": "publicada", "comentario": "✔"}
    r = client.post(
        "/preguntas/batch/decision",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["procesadas"] == len(ids)
