"""
CRUD muy simple para el catálogo Isla.
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..models import Isla


# ────────────────────────────────────────────────
def list_all(db: Session) -> list[Isla]:
    return db.query(Isla).all()


def get_one(db: Session, id_isla: int) -> Isla | None:
    return db.get(Isla, id_isla)


def create_isla(
    db: Session,
    nombre: str,
    descripcion: str | None = None,
) -> Isla:
    isla = Isla(nombre=nombre, descripcion=descripcion)
    db.add(isla)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(f"Ya existe una isla con nombre '{nombre}'") from exc
    db.refresh(isla)
    return isla
