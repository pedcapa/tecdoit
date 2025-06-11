# tests/test_crud_opciones.py
from sqlalchemy.orm import Session
from app.models import Isla
from app.crud import opciones as crud_opciones, preguntas as crud_preguntas
from app.schemas import OpcionCreate, PreguntaCreate


def test_crud_opciones(db_session: Session, test_user):
    # ─── Asegurar que exista la isla con id_isla=1 ──────────────────────────
    if not db_session.get(Isla, 1):
        db_session.add(Isla(id_isla=1, nombre="Isla 1", descripcion="Descripción de isla 1"))
        db_session.commit()

    # 1) Crear pregunta con al menos DOS opciones iniciales
    p_payload = PreguntaCreate(
        enunciado="¿Test 1+1?",
        tipo="abc",
        id_isla=1,
        dificultad=1,
        randomizar=False,
        temas=[],
        opciones=[
            OpcionCreate(texto="Uno", es_correcta=False),
            OpcionCreate(texto="Dos", es_correcta=True),
        ]
    )
    pregunta = crud_preguntas.create_pregunta(
        db_session, p_payload, test_user.id_profesor
    )
    assert pregunta.id_pregunta is not None

    # 2) Create opción adicional
    new_opt = OpcionCreate(texto="Tres", es_correcta=False)
    opcion = crud_opciones.create_opcion(
        db_session, pregunta.id_pregunta, test_user.id_profesor, new_opt
    )
    assert opcion.id_opcion is not None
    assert opcion.id_pregunta == pregunta.id_pregunta

    # 3) Update esa opción
    up_payload = OpcionCreate(texto="Tres (editada)", es_correcta=False)
    updated = crud_opciones.update_opcion(db_session, opcion.id_opcion, up_payload)
    assert updated.texto == "Tres (editada)"

    # 4) Delete la opción recién creada
    crud_opciones.delete_opcion(db_session, opcion.id_opcion)
    from app.models import Opcion
    assert db_session.get(Opcion, opcion.id_opcion) is None
