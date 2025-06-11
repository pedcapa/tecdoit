from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from ..config import STATIC_DIR, BASE_URL
from pathlib import Path

from .. import schemas, crud, models
from ..deps import get_current_user, get_db, is_admin

router = APIRouter(prefix="/profesores", tags=["Profesores"])

@router.post("/me/avatar", response_model=schemas.ProfesorOut)
async def upload_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    avatars_dir = Path(STATIC_DIR) / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)

    ext = avatar.filename.rsplit(".", 1)[-1]
    filename = f"{user.id_profesor}.{ext}"
    save_path = avatars_dir / filename
    contents = await avatar.read()
    save_path.write_bytes(contents)

    avatar_url = f"{BASE_URL}/img/avatars/{filename}"

    updated = crud.profesor.patch_profesor(
        db,
        user.id_profesor,
        {"avatar_url": avatar_url}
    )
    if not updated:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el avatar")
    return updated


# --------------------------------------------------------------------------- #
#  Perfil propio
# --------------------------------------------------------------------------- #
@router.get("/me", response_model=schemas.ProfesorOut)
def me(user: models.Profesor = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=schemas.ProfesorOut)
def edit_me(
    payload: schemas.ProfesorBase,
    db: Session = Depends(get_db),
    user: models.Profesor = Depends(get_current_user),
):
    prof = crud.profesor.patch_profesor(db, user.id_profesor, payload.model_dump(exclude_unset=True))
    return prof


# --------------------------------------------------------------------------- #
#  Admin
# --------------------------------------------------------------------------- #
@router.get("/", response_model=list[schemas.ProfesorOut], dependencies=[Depends(is_admin)])
def list_profesores(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.profesor.list_profesores(db, skip, limit)


@router.get("/{id_prof}", response_model=schemas.ProfesorOut, dependencies=[Depends(is_admin)])
def get_prof(id_prof: int, db: Session = Depends(get_db)):
    prof = db.get(models.Profesor, id_prof)
    if not prof:
        raise HTTPException(404, "No encontrado")
    return prof


@router.patch("/{id_prof}", response_model=schemas.ProfesorOut, dependencies=[Depends(is_admin)])
def patch_prof(id_prof: int, payload: dict, db: Session = Depends(get_db)):
    return crud.profesor.patch_profesor(db, id_prof, payload)

