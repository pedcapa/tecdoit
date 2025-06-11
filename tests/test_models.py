# tests/test_models.py

import os
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# 1) Usa SQLite en memoria para evitar errores de drop_all y FK
TEST_URL = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
engine = create_engine(TEST_URL, future=True)
SessionLocal = sessionmaker(bind=engine)

# 2) Fixtures que crean y destruyen las tablas
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # import tardío de Base para registrar todas las clases declarativas
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    yield
    # Drop sin errores en SQLite
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db():
    session = SessionLocal()
    yield session
    session.close()

# 3) Pruebas

def test_tables_exist():
    insp = inspect(engine)
    expected = {"isla", "tema", "profesor",
                "pregunta", "opcion", "pregunta_tema", "decision"}
    assert expected.issubset(set(insp.get_table_names()))

def test_insert_profesor(db):
    from app.models import Profesor
    prof = Profesor(
        nombre="Ada", apellido="Lovelace",
        correo="ada@test.mx", pwd="x", rol="admin"
    )
    db.add(prof)
    db.commit()
    assert prof.id_profesor is not None

def test_enum_pregunta_tipo():
    # Accede al Enum real definido en la columna
    from app.models import Pregunta
    # Column object:
    col = Pregunta.__table__.c.tipo
    enums = set(col.type.enums)  # aquí sí funciona
    assert enums == {"abc", "vf", "checkbox"}
