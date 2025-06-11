# app/routers/opciones.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/preguntas/{pid}/opciones", tags=["Opciones"])

@router.post("/", response_model=schemas.OpcionOut)
def add(pid: int, payload: schemas.OpcionCreate,
        db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.opciones.create_opcion(db, pid, user.id_profesor, payload)

@router.patch("/{id_opcion}", response_model=schemas.OpcionOut)
def patch(pid:int, id_opcion:int, payload:schemas.OpcionCreate,
          db:Session=Depends(get_db), user=Depends(get_current_user)):
    opt = db.get(models.Opcion, id_opcion)
    if not opt or opt.id_profesor != user.id_profesor:
        raise HTTPException(404)
    return crud.opciones.update_opcion(db, id_opcion, payload)

@router.delete("/{id_opcion}", status_code=204)
def delete(pid:int, id_opcion:int,
           db:Session=Depends(get_db), user=Depends(get_current_user)):
    crud.opciones.delete_opcion(db, id_opcion)
