"""
Inserta la revisión y actualiza el estado de la pregunta.
"""
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..models import Decision, Pregunta
from ..schemas import DecisionCreate
from .. import models, schemas


def create_decision(
    db: Session,
    id_pregunta: int,
    id_profesor: int,
    payload: schemas.DecisionCreate,
) -> Decision:
    preg = db.get(Pregunta, id_pregunta)
    if not preg:
        raise ValueError("Pregunta no encontrada")

    decision = Decision(
        id_pregunta=id_pregunta,
        id_profesor=id_profesor,
        fecha=datetime.now(timezone.utc),
        decision=payload.decision,
        comentario=payload.comentario,
    )
    db.add(decision)
    preg.estado = payload.decision          # sincroniza estado

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            f"Ya existe una decisión '{payload.decision}' para esta pregunta"
        ) from exc

    db.refresh(decision)
    return decision


# Helpers de lectura
def list_by_pregunta(db: Session, id_pregunta: int):
    return (
        db.query(Decision)
        .filter(Decision.id_pregunta == id_pregunta)
        .order_by(Decision.fecha.desc())
        .all()
    )
