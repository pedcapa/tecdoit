# tests/test_config.py
from pathlib import Path
from app import config

def test_env_vars():
    assert config.DATABASE_URL, "DATABASE_URL no definido"
    assert config.DATABASE_URL_TEST, "DATABASE_URL_TEST no definido"
    assert config.SECRET_KEY != "insecure-key", "SECRET_KEY default => .env no cargó"

def test_types():
    assert isinstance(config.PREVIEW_TTL, int)
    assert isinstance(config.STATIC_DIR, Path)

def test_dirs_exist(tmp_path, monkeypatch):
    # usa directorio temporal para no tocar tu FS real
    monkeypatch.setattr(config, "STATIC_DIR", tmp_path / "static")
    monkeypatch.setattr(config, "PREVIEW_DIR", tmp_path / "previews")
    for d in (config.STATIC_DIR, config.PREVIEW_DIR):
        d.mkdir(parents=True, exist_ok=True)
        assert d.exists()
