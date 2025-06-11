from sqlalchemy.orm import Session

from app.crud import preguntas as crud_preguntas
from app.schemas import PreguntaCreate, OpcionCreate
from app.models import Isla


def test_crud_preguntas(db_session, test_user):
    # crear isla 1 si no existe
    if not db_session.get(Isla, 1):
        db_session.add(Isla(id_isla=1, nombre="Isla 1"))
        db_session.commit()
    # 1) Create pregunta con opciones
    p_payload = PreguntaCreate(
        enunciado="¿Cuánto es 3+4?",
        tipo="abc",
        id_isla=1,
        dificultad=2,
        randomizar=True,
        temas=[],
        opciones=[
            OpcionCreate(texto="6", es_correcta=False),
            OpcionCreate(texto="7", es_correcta=True),
        ]
    )
    pregunta = crud_preguntas.create_pregunta(
        db_session, p_payload, test_user.id_profesor
    )
    assert pregunta.id_pregunta is not None

    # 2) List all
    todas = crud_preguntas.get_preguntas(db_session)
    assert any(p.id_pregunta == pregunta.id_pregunta for p in todas)

    # 3) Filter por estado
    borradores = crud_preguntas.get_preguntas(
        db_session, estado="borrador"
    )
    assert any(p.id_pregunta == pregunta.id_pregunta for p in borradores)

    # 4) Filter por tipo
    abcs = crud_preguntas.get_preguntas(
        db_session, tipo="abc"
    )
    assert any(p.id_pregunta == pregunta.id_pregunta for p in abcs)
