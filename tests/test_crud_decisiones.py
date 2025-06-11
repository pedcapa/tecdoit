from sqlalchemy.orm import Session
from app.models import Isla
from app.crud import decisiones as crud_decisiones, preguntas as crud_preguntas
from app.schemas import DecisionCreate, PreguntaCreate, OpcionCreate


def test_crud_decisiones(db_session: Session, test_user):
    # ─── Asegurar que exista la isla con id_isla=1 ──────────────────────────
    if not db_session.get(Isla, 1):
        db_session.add(Isla(id_isla=1, nombre="Isla 1", descripcion="Prueba"))
        db_session.commit()

    # 1) Crear pregunta CON DOS OPCIONES MÍNIMAS
    p_payload = PreguntaCreate(
        enunciado="¿Decidirás?",
        tipo="abc",
        id_isla=1,
        dificultad=2,
        randomizar=False,
        temas=[],
        opciones=[
            OpcionCreate(texto="Opción A", es_correcta=False),
            OpcionCreate(texto="Opción B", es_correcta=True),
        ]
    )
    pregunta = crud_preguntas.create_pregunta(
        db_session, p_payload, test_user.id_profesor
    )

    # 2) Crear decision
    d_payload = DecisionCreate(decision="publicada", comentario="OK")
    decision = crud_decisiones.create_decision(
        db_session, pregunta.id_pregunta, test_user.id_profesor, d_payload
    )
    assert decision.id_revision is not None
    assert decision.decision == "publicada"
    # Verificar que la decisión guarda correctamente el revisor
    assert decision.id_profesor == test_user.id_profesor

    # 3) List by pregunta
    list_p = crud_decisiones.list_by_pregunta(db_session, pregunta.id_pregunta)
    assert any(d.id_revision == decision.id_revision for d in list_p)
