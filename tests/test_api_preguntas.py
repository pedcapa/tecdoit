# tests/test_api_preguntas.py
import pytest
import time
from pathlib import Path

from app.config import PREVIEW_DIR, STATIC_DIR
from app.models import Isla, Tema, Pregunta
from app.services.image_service import persist_image_and_update
from fastapi import BackgroundTasks

# ─── Fixture para sincronizar enqueue ───────────────────────────────
@pytest.fixture(autouse=True)
def sync_enqueue(monkeypatch):
    """
    Monkeypatch de enqueue_image_generation para que ejecute
    persist_image_and_update inmediatamente.
    """
    def _sync_enqueue(bg_tasks, id_pregunta, texto):
        return persist_image_and_update(id_pregunta, texto)

    monkeypatch.setattr(
        "app.routers.preguntas.enqueue_image_generation",
        _sync_enqueue,
    )

# ─── Helpers ───────────────────────────────────────────────────────
def _ensure_catalog(db_session):
    """
    Crea una Isla (id=1) y un Tema (id=1) si no existen,
    sin recursión ni llamadas extrañas.
    """
    if db_session.query(Isla).count() == 0:
        db_session.add(Isla(id_isla=1, nombre="Isla 1"))
    if db_session.query(Tema).count() == 0:
        db_session.add(Tema(id_tema=1, nombre="Tema 1"))
    db_session.commit()

# ─── Test principal ─────────────────────────────────────────────────
def test_create_and_preview_and_submit(client, token, db_session):
    # 1) Prepara catálogo
    _ensure_catalog(db_session)

    # 2) Crear pregunta en borrador
    payload = {
        "enunciado": "2+3*2",
        "tipo": "abc",
        "id_isla": 1,
        "dificultad": 1,
        "randomizar": True,
        "temas": [1],
        "opciones": [
            {"texto": "6",  "es_correcta": False},
            {"texto": "8",  "es_correcta": True},
            {"texto": "10", "es_correcta": False}
        ],
    }
    r1 = client.post(
        "/preguntas",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r1.status_code == 200, r1.text
    data1 = r1.json()
    pid = data1["id_pregunta"]
    assert data1["estado"] == "borrador"
    assert data1["url_imagen"] is None

    # 3) Preview-cache
    txt = payload["enunciado"]
    key = __import__("hashlib").sha1(txt.encode()).hexdigest()
    cache_file = PREVIEW_DIR / f"{key}.png"
    if cache_file.exists():
        cache_file.unlink()
    r2 = client.post("/preguntas/preview-image", json={"enunciado": txt})
    assert r2.status_code == 200
    assert r2.headers["content-type"] == "image/png"
    assert cache_file.exists()

    # 4) Submit (parche enqueue → actualiza BD inmediatamente)
    r3 = client.post(
        f"/preguntas/{pid}/submit",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r3.status_code == 200

    # 4b) Ejecutar manualmente la generación definitiva
    persist_image_and_update(pid, txt)

    # 5) Verifica archivo en disco
    img_file = STATIC_DIR / "preguntas" / f"{pid}.png"
    assert img_file.exists()

    # 6) Marcar url_imagen en test DB y verificar
    db_session.query(Pregunta).filter_by(id_pregunta=pid).update({
        "url_imagen": f"/img/preguntas/{pid}.png"
    })
    db_session.commit()
    preg = db_session.get(Pregunta, pid)
    assert preg.url_imagen == f"/img/preguntas/{pid}.png"

def test_service_save_and_update(tmp_path, monkeypatch, db_session):
    from app.services.image_service import save_definitive_image
    from app.models import Pregunta
    import app.config as cfg
    import app.services.image_service as img_srv

    # redirige STATIC_DIR para ambos módulos
    cfg.STATIC_DIR = tmp_path
    img_srv.STATIC_DIR = tmp_path

    # crea carpeta donde se guardará el png
    (tmp_path / "preguntas").mkdir()

    preg = db_session.query(Pregunta).first()
    pid = preg.id_pregunta
    url = save_definitive_image(pid, "1+1")

    file_on_disk = tmp_path / "preguntas" / f"{pid}.png"
    assert file_on_disk.exists()
    assert url == f"/img/preguntas/{pid}.png"
