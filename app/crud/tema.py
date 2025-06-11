"""
CRUD para Tema con control de nombre único.
"""
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..models import Tema


def list_temas(db: Session) -> List[Tema]:
    return db.query(Tema).all()


def get_tema(db: Session, id_tema: int) -> Tema | None:
    return db.get(Tema, id_tema)


def create_tema(db: Session, nombre: str, descripcion: str | None) -> Tema:
    tema = Tema(nombre=nombre, descripcion=descripcion)
    db.add(tema)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(f"El tema '{nombre}' ya existe") from exc
    db.refresh(tema)
    return tema


def patch_tema(db: Session, id_tema: int, data: dict) -> Tema:
    tema = db.get(Tema, id_tema)
    if not tema:
        raise ValueError("Tema no encontrado")

    for k, v in data.items():
        setattr(tema, k, v)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Ese nombre de tema ya existe") from exc

    db.refresh(tema)
    return tema


def delete_tema(db: Session, id_tema: int) -> None:
    db.query(Tema).filter(Tema.id_tema == id_tema).delete()
    db.commit()
