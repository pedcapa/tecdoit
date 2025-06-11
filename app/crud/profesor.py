"""
CRUD Profesor.
Aquí garantizamos que la sesión que se pasa como parámetro
sea la misma usada para todos los commits y consultas.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models, schemas
from ..utils.hashing import get_password_hash


def get_by_email(db: Session, correo: str) -> Optional[models.Profesor]:
    """Busca un profesor por su correo."""
    return (
        db.query(models.Profesor)
          .filter(models.Profesor.correo == correo)
          .first()
    )


def create_profesor(
    db: Session,
    payload: schemas.ProfesorCreate
) -> models.Profesor:
    """
    Crea un nuevo profesor:
    - Hashea la contraseña.
    - Usa la misma sesión 'db' para add/commit/refresh.
    """
    data = payload.model_dump(exclude={"pwd"}, exclude_unset=True)
    data["pwd"] = get_password_hash(payload.pwd)
    prof = models.Profesor(**data)
    db.add(prof)
    db.commit()         # Persiste en la BD asociada a 'db'
    db.refresh(prof)    # Refresca 'prof' con el id autogenerado
    return prof


def list_profesores(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> List[models.Profesor]:
    """
    Devuelve todos los profesores, ordenados por su PK, con paginación.
    El 'order_by' garantiza que el test encuentre el registro creado.
    """
    return (
        db.query(models.Profesor)
          .order_by(models.Profesor.id_profesor)
          .offset(skip)
          .limit(limit)
          .all()
    )


def patch_profesor(
    db: Session,
    id_prof: int,
    data: dict
) -> models.Profesor:
    """Actualiza campos en el perfil de un profesor existente."""
    prof = db.get(models.Profesor, id_prof)
    for k, v in data.items():
        setattr(prof, k, v)
    db.commit()
    db.refresh(prof)
    return prof
