import pytest
from pydantic import ValidationError
from app.schemas import (
    PreguntaCreate, PreguntaOut,
    OpcionCreate,
    ProfesorCreate, ProfesorOut
)

def test_pregunta_create_valid():
    payload = {
        "enunciado": "¿Cuál es el resultado de 2+3?",
        "tipo": "abc",
        "id_isla": 2,
        "dificultad": 1,
        "randomizar": True,
        "temas": [1, 2],
        "opciones": [
            {"texto": "6",  "es_correcta": False},
            {"texto": "5",  "es_correcta": True},
            {"texto": "10", "es_correcta": False},
        ]
    }
    pc = PreguntaCreate(**payload)
    # comprueba que los valores se asignan correctamente
    assert pc.enunciado.startswith("¿Cuál")
    assert pc.tipo == "abc"
    assert pc.dificultad == 1
    assert isinstance(pc.opciones, list)
    assert all(isinstance(o, OpcionCreate) for o in pc.opciones)

def test_pregunta_create_invalid_tipo():
    payload = {
        "enunciado": "2+2?",
        "tipo": "multiple",   # inválido
        "id_isla": 1,
        "dificultad": 1,
        "randomizar": False,
        "temas": [],
        "opciones": [{"texto":"4","es_correcta":True}],
    }
    with pytest.raises(ValidationError) as exc:
        PreguntaCreate(**payload)
    # confirma que el error menciona "tipo"
    assert "tipo" in str(exc.value)

def test_profesor_create_and_out_mode():
    # entrada válida
    input_data = {
        "nombre": "Alan",
        "apellido": "Turing",
        "correo": "alan@computing.org",
        "pwd": "segura123",
        "rol": "autor",
        "campus": None,
        "titulo": None,
        "cargo": None,
        "bio": None,
        "avatar_url": None,
    }
    pcreate = ProfesorCreate(**input_data)
    assert pcreate.correo == "alan@computing.org"
    assert pcreate.rol == "autor"

    # simulamos un OBJETO ORM con atributos análogos
    class DummyORM:
        id_profesor = 42
        nombre = "Alan"
        apellido = "Turing"
        correo = "alan@computing.org"
        campus = None
        titulo = None
        cargo = None
        bio = None
        avatar_url = None
        rol = "autor"
        activo = True

    orm = DummyORM()
    pout = ProfesorOut.model_validate(orm)
    assert pout.id_profesor == 42
    assert pout.correo == "alan@computing.org"
    assert pout.activo is True

def test_profesor_create_invalid_email():
    bad = {
        "nombre": "Ada",
        "apellido": "Lovelace",
        "correo": "no-es-un-email",
        "pwd": "xyz123",
        "rol": "autor"
    }
    with pytest.raises(ValidationError):
        ProfesorCreate(**bad)
