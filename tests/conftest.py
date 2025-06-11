import os, tempfile
import pytest
import uuid
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from pathlib import Path
from sqlalchemy import text, create_engine

SEED_SQL = Path(__file__).resolve().parent.parent / "app" / "seed_static.sql"

# ----- FUENTES -----
from app import config
from app.database import get_db, Base
from app.models import Profesor, Isla
from app.main import app
from app.utils.hashing import get_password_hash
from app.utils.security import create_access_token

# ----- BD DE PRUEBA -----
@pytest.fixture(scope="session", autouse=True)
def override_settings():
    """
    Asegura que siempre usemos la BD de pruebas declarada en .env.test
    """
    os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]
    config.DATABASE_URL = os.environ["DATABASE_URL_TEST"]
    yield


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(config.DATABASE_URL_TEST, pool_pre_ping=True)

    # Crea todas las tablas del modelo
    Base.metadata.create_all(bind=eng)

    # ——— Reinicia catálogos y carga seed ——————————————
    with eng.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        conn.execute(text("TRUNCATE Isla"))
        conn.execute(text("TRUNCATE Tema"))
        conn.execute(text("TRUNCATE Profesor"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

        sql = SEED_SQL.read_text(encoding="utf-8")
        # Divide en sentencias y ejecuta individuales
        for stmt in filter(None, (s.strip() for s in sql.split(";"))):
            conn.execute(text(stmt))
    yield eng
    eng.dispose()

@pytest.fixture()
def db_session(engine):
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# ----- USUARIO DE PRUEBA -----
@pytest.fixture()
def test_user(db_session: Session):
    # Generamos un email único para evitar collisions
    unique_email = f"ada-{uuid.uuid4().hex}@test.mx"
    user = Profesor(
        nombre="Ada",
        apellido="Lovelace",
        correo=unique_email,
        pwd=get_password_hash("secret"),
        rol="admin",
        activo=True,
    )
    db_session.add(user)
    db_session.flush()
    return user

@pytest.fixture()
def token(test_user):
    return create_access_token(
        {"id_profesor": test_user.id_profesor, "rol": test_user.rol}
    )

# ----- CLIENT -----
@pytest.fixture()
def client(db_session: Session, monkeypatch):
    """Inyecta la sesión de pruebas en FastAPI."""
    def _get_db_override():
        yield db_session
    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
