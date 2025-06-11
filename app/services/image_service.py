"""
Funciones de renderizado + caché de previews + guardado definitivo.
"""
import hashlib, os, time
from pathlib import Path
from typing import Tuple

from ..config import STATIC_DIR, PREVIEW_DIR, PREVIEW_TTL, BASE_URL
from ..database import SessionLocal
from ..models import Pregunta
from ..routers.txt_to_img import render_png          # reutiliza tu lógica

PREVIEW_DIR.mkdir(exist_ok=True, parents=True)
(STATIC_DIR / "preguntas").mkdir(exist_ok=True, parents=True)

def _hash(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()

def get_or_cache_preview(texto: str) -> bytes:
    key = _hash(texto)
    path = PREVIEW_DIR / f"{key}.png"
    if path.exists() and time.time() - path.stat().st_mtime <= PREVIEW_TTL:
        return path.read_bytes()
    png = render_png(texto)
    path.write_bytes(png)
    return png

def save_definitive_image(id_pregunta: int, texto: str) -> str:
    """Genera y guarda la imagen → devuelve url relativa."""
    png = render_png(texto)
    dest = STATIC_DIR / "preguntas" / f"{id_pregunta}.png"
    dest.write_bytes(png)
    return f"/img/preguntas/{id_pregunta}.png"

def persist_image_and_update(id_pregunta: int, texto: str):
    """Función llamada desde tarea en background."""
    url = save_definitive_image(id_pregunta, texto)
    db = SessionLocal()
    preg = db.get(Pregunta, id_pregunta)
    if preg:
        preg.url_imagen = url
        db.commit()
    db.close()
