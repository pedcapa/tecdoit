from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..deps import get_db, is_admin

router = APIRouter(prefix="/temas", tags=["Temas"])


@router.get("/", response_model=list[schemas.TemaOut])
def list_temas(db: Session = Depends(get_db)):
    return crud.tema.list_temas(db)


@router.post("/", response_model=schemas.TemaOut, dependencies=[Depends(is_admin)])
def create_tema(payload: schemas.TemaCreate, db: Session = Depends(get_db)):
    return crud.tema.create_tema(db, payload.nombre, payload.descripcion)


@router.patch("/{id_tema}", response_model=schemas.TemaOut, dependencies=[Depends(is_admin)])
def patch_tema(id_tema: int, payload: dict, db: Session = Depends(get_db)):
    tema = crud.tema.patch_tema(db, id_tema, payload)
    if not tema:
        raise HTTPException(404, "No encontrado")
    return tema


@router.delete("/{id_tema}", status_code=204, dependencies=[Depends(is_admin)])
def delete_tema(id_tema: int, db: Session = Depends(get_db)):
    crud.tema.delete_tema(db, id_tema)
