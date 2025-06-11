from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Isla
from ..schemas import IslaOut

from .. import schemas, crud
from ..deps import is_admin

router = APIRouter(prefix="/islas", tags=["Islas"])

@router.get("", response_model=list[IslaOut])
def list_islas(db: Session = Depends(get_db)):
    return db.query(Isla).all()

@router.get("/{id_isla}", response_model=IslaOut)
def get_isla(id_isla: int, db: Session = Depends(get_db)):
    return db.get(Isla, id_isla)

@router.post(
    "/",
    response_model=schemas.IslaOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(is_admin)]
)
def create_isla(
    payload: schemas.IslaOut,  # o define un IslaCreate si prefieres separar I/O
    db: Session = Depends(get_db),
):
    try:
        return crud.isla.create_isla(
            db,
            nombre=payload.nombre,
            descripcion=payload.descripcion,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Opcional: actualización parcial
@router.patch(
    "/{id_isla}",
    response_model=schemas.IslaOut,
    dependencies=[Depends(is_admin)]
)
def update_isla(
    id_isla: int,
    payload: schemas.IslaOut,  # o un IslaUpdate con todos Optional[]
    db: Session = Depends(get_db),
):
    isla = crud.isla.get_one(db, id_isla)
    if not isla:
        raise HTTPException(404, "Isla no encontrada")
    if payload.nombre is not None:
        isla.nombre = payload.nombre
    if payload.descripcion is not None:
        isla.descripcion = payload.descripcion
    db.commit(); db.refresh(isla)
    return isla

# Opcional: borrado lógico o físico
@router.delete(
    "/{id_isla}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(is_admin)]
)
def delete_isla(id_isla: int, db: Session = Depends(get_db)):
    isla = crud.isla.get_one(db, id_isla)
    if not isla:
        raise HTTPException(404, "Isla no encontrada")
    db.delete(isla)
    db.commit()