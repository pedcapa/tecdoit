# app/crud/opciones.py
"""
CRUD de Opcion: creación, edición y borrado sin dependencias de relaciones directas.
"""
from sqlalchemy.orm import Session
from .. import models, schemas

def create_opcion(
    db: Session,
    id_pregunta: int,
    autor_id: int,
    payload: schemas.OpcionCreate,
) -> models.Opcion:
    """
    Inserta una nueva opción vinculada a la pregunta indicada.
    """
    opcion = models.Opcion(
        id_pregunta=id_pregunta,
        texto=payload.texto,
        es_correcta=payload.es_correcta,
        id_profesor=autor_id,
    )
    db.add(opcion)
    db.commit()
    db.refresh(opcion)
    return opcion

def update_opcion(
    db: Session,
    id_opcion: int,
    payload: schemas.OpcionCreate,
) -> models.Opcion:
    """
    Actualiza el texto y marca correcta/incorrecta de una opción existente.
    """
    opcion = db.get(models.Opcion, id_opcion)
    if not opcion:
        raise ValueError("Opción inexistente")
    opcion.texto = payload.texto
    opcion.es_correcta = payload.es_correcta
    db.commit()
    db.refresh(opcion)
    return opcion

def delete_opcion(db: Session, id_opcion: int) -> None:
    """
    Elimina la opción indicada.
    """
    opcion = db.get(models.Opcion, id_opcion)
    if not opcion:
        return
    db.delete(opcion)
    db.commit()
