"""
tests/test_txt_to_img.py
------------------------
Pruebas para el router txt_to_img:
- healthcheck (ping)
- error por texto vacío
- generación de PNG para texto simple y con LaTeX
- manejo de excepción en render
"""

import io
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.routers.txt_to_img import render_png, router as txt_router

# Montamos el router explicitamente (si no está incluido en main)
app.include_router(txt_router, prefix="/txt_to_img")


@pytest.fixture
def client():
    return TestClient(app)


def test_ping(client):
    resp = client.get("/txt_to_img/ping")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_empty_text_returns_422(client):
    resp = client.post("/txt_to_img/", json={"text": ""})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_plain_text_renders_png(client):
    payload = {"text": "Hola mundo"}
    resp = client.post("/txt_to_img/", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    # Verificamos que la respuesta tiene bytes de PNG
    content = resp.content
    assert content.startswith(b"\x89PNG\r\n\x1a\n")


def test_simple_latex_renders_png(client):
    # Una fórmula sencilla
    payload = {"text": "E = mc^2"}
    resp = client.post("/txt_to_img/", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    # Debe contener cabecera válida
    assert resp.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_exception_propagates(client, monkeypatch):
    from app.routers.txt_to_img import MINIMAL_PNG
    # Forzamos que render_png levante excepción
    def fake_render(txt):
        raise RuntimeError("boom")
    monkeypatch.setattr("app.routers.txt_to_img.render_png", fake_render)

    resp = client.post("/txt_to_img/", json={"text": "x"})

    assert resp.status_code == 200
    assert resp.content == MINIMAL_PNG
