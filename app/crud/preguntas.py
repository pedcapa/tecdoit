"""
Funciones CRUD de Pregunta (+ filtros paginados).
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from .. import models

def create_pregunta(db: Session, payload, autor_id: int) -> models.Pregunta:
    pregunta = models.Pregunta(
        enunciado  = payload.enunciado,
        tipo       = payload.tipo,
        id_isla    = payload.id_isla,
        dificultad = payload.dificultad,
        randomizar = payload.randomizar,
        id_profesor= autor_id,
    )
    # Temas
    for id_tema in payload.temas:
        tema = db.get(models.Tema, id_tema)
        if tema:
            pregunta.temas.append(tema)
    db.add(pregunta); db.flush()

    # Opciones
    for opt in payload.opciones:
        db.add(models.Opcion(
            id_pregunta = pregunta.id_pregunta,
            texto       = opt.texto,
            es_correcta = opt.es_correcta,
            id_profesor = autor_id
        ))
    db.commit(); db.refresh(pregunta)
    return pregunta

from typing import Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from .. import models

def get_preguntas(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    estado: Optional[str] = None,
    tipo: Optional[str] = None,
    id_isla: Optional[int] = None,
    dificultad: Optional[int] = None,
    autor: Optional[int] = None,
):
    q = (
        db.query(models.Pregunta)
        .options(joinedload(models.Pregunta.opciones))
        .order_by(desc(models.Pregunta.id_pregunta))          # ← NUEVO
    )
    if estado:
        q = q.filter(models.Pregunta.estado == estado)
    if tipo:
        q = q.filter(models.Pregunta.tipo == tipo)
    if id_isla:
        q = q.filter(models.Pregunta.id_isla == id_isla)
    if dificultad:
        q = q.filter(models.Pregunta.dificultad == dificultad)
    if autor is not None:
        q = q.filter(models.Pregunta.id_profesor == autor)
    return q.offset(skip).limit(limit).all()


def get_pregunta_detalle(db: Session, id_: int) -> models.Pregunta | None:
    stmt = (
        select(models.Pregunta)
        .options(
            joinedload(models.Pregunta.opciones),
            joinedload(models.Pregunta.temas),
            joinedload(models.Pregunta.decisiones),
        )
        .where(models.Pregunta.id_pregunta == id_)
    )
    return db.execute(stmt).scalars().first()


def update_pregunta(db: Session, id_: int, data: dict) -> models.Pregunta:
    preg = db.get(models.Pregunta, id_)
    # Campos simples
    for k in ("enunciado","tipo","id_isla","dificultad","randomizar"):
        if k in data:
            setattr(preg, k, data[k])
    # Temas: reemplazar la relación
    if "temas" in data:
        preg.temas = [
            db.get(models.Tema, tid) for tid in data["temas"]
            if db.get(models.Tema, tid)
        ]
    # Opciones: podrías borrarlas y recrear según data["opciones"]
    if "opciones" in data:
        preg.opciones.clear()
        for o in data["opciones"]:
            preg.opciones.append(models.Opcion(
                texto=o["texto"],
                es_correcta=o["es_correcta"],
                id_profesor=preg.id_profesor
            ))
    db.commit()
    db.refresh(preg)
    return preg
