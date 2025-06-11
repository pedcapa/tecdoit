"""
Login + alta de profesor (admin).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..deps import is_admin, get_current_user
from ..utils import hashing, security

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user: models.Profesor = (
        db.query(models.Profesor)
        .filter(models.Profesor.correo == form.username)
        .first()
    )
    if not user or not hashing.verify_password(form.password, user.pwd):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    token = security.create_access_token(
        {"id_profesor": user.id_profesor, "rol": user.rol}
    )
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.ProfesorOut,
             dependencies=[Depends(is_admin)])
def register_profesor(payload: schemas.ProfesorCreate,
                      db: Session = Depends(get_db)):
    if db.query(models.Profesor).filter(
            models.Profesor.correo == payload.correo).first():
        raise HTTPException(400, "Correo ya existe")
    hashed = hashing.get_password_hash(payload.pwd)
    prof = models.Profesor(**payload.model_dump(exclude={"pwd"}), pwd=hashed)
    db.add(prof); db.commit(); db.refresh(prof)
    return prof

@router.post(
    "/change-password",
    summary="Permite a un usuario autenticado cambiar su propia contraseña"
)
def change_password(
    payload: schemas.ChangePassword,
    db: Session = Depends(get_db),
    user: models.Profesor = Depends(get_current_user),
):
    # 1) Verificar que la contraseña actual coincida
    if not hashing.verify_password(payload.old_password, user.pwd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    # 2) Hashear la nueva y actualizar en BD
    user.pwd = hashing.get_password_hash(payload.new_password)
    db.commit()

    return {"msg": "Contraseña actualizada exitosamente"}