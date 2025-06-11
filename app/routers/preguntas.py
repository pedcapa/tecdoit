from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response, Query
from sqlalchemy.orm import Session

from pydantic import BaseModel

from .. import schemas, crud, models
from ..crud import decisiones as crud_decision
from ..deps import get_current_user, get_db, is_admin
from ..services.image_service import get_or_cache_preview
from ..tasks.background import enqueue_image_generation

router = APIRouter(prefix="/preguntas", tags=["Preguntas"])

# ─── MODELOS DE BODY ────────────────────────────────────────────────
class BatchIDs(BaseModel):
    ids: list[int]

class BatchDecision(BatchIDs):
    decision: str
    comentario: str | None = None

# ─── MODELOS PARA BATCH ────────────────────────────────────────────────
@router.post("/batch/submit")
def batch_submit(
    payload: BatchIDs,                       # ← ahora es un modelo
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    enviadas = 0
    for pid in payload.ids:
        preg = db.get(models.Pregunta, pid)
        if preg and preg.id_profesor == user.id_profesor and preg.estado == "borrador":
            preg.estado = "en revisión"
            enqueue_image_generation(background, pid, preg.enunciado)
            enviadas += 1
    db.commit()
    return {"enviadas": enviadas}

# ─── RUTA batch/decision ────────────────────────────────────────────
@router.post("/batch/decision", dependencies=[Depends(is_admin)])
def batch_decision(
    payload: BatchDecision,                  # ← modelo con decision + comentario
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    processed = 0
    for pid in payload.ids:
        preg = db.get(models.Pregunta, pid)
        if preg and preg.estado == "en revisión":
            if preg.id_profesor == user.id_profesor:
                continue
            crud_decision.create_decision(db, pid, user.id_profesor, payload)
            processed += 1
    return {"procesadas": processed}

# ——— Preview ——————————————————————————————————————————
@router.post("/preview-image", response_class=Response,
             responses={200: {"content": {"image/png": {}}}})
def preview(payload: schemas.PreviewIn):
    png = get_or_cache_preview(payload.enunciado)
    return Response(content=png, media_type="image/png")

# ——— Crear ————————————————————————————————————————————
@router.post("/", response_model=schemas.PreguntaOut)
def create(p: schemas.PreguntaCreate,
           db: Session = Depends(get_db),
           user = Depends(get_current_user)):
    return crud.preguntas.create_pregunta(db, p, autor_id=user.id_profesor)

@router.get("/", response_model=list[schemas.PreguntaOut])
def list_preguntas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    estado: str | None = None,
    tipo: str | None = None,
    id_isla: int | None = None,
    dificultad: int | None = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    skip = (page - 1) * size
    autor_id = None if user.rol == "admin" else user.id_profesor
    return crud.preguntas.get_preguntas(
        db,               # db
        skip,             # skip
        size,             # limit
        estado,           # estado
        tipo,             # tipo
        id_isla,          # id_isla
        dificultad,       # dificultad
        autor=autor_id    # autor
    )

@router.get("/{id:int}", response_model=schemas.PreguntaOut)
def detalle(id: int,
            db: Session = Depends(get_db),
            user = Depends(get_current_user)):
    preg = crud.preguntas.get_pregunta_detalle(db, id)
    if not preg:
        raise HTTPException(404)
    if user.rol != "admin" and preg.id_profesor != user.id_profesor:
        raise HTTPException(403)
    return preg


@router.patch("/{id:int}", response_model=schemas.PreguntaOut)
def editar(id: int,
           payload: schemas.PreguntaCreate,
           db: Session = Depends(get_db),
           user = Depends(get_current_user)):
    preg = db.get(models.Pregunta, id)
    if not preg or preg.id_profesor != user.id_profesor:
        raise HTTPException(404)
    if preg.estado != "borrador":
        raise HTTPException(400, "Solo se puede editar borrador")
    return crud.preguntas.update_pregunta(db, id, payload.model_dump(exclude_unset=True))


# ——— Submit ——————————————————————————————————————————
@router.post("/{id:int}/submit")
def submit(id: int,
           background: BackgroundTasks,
           db: Session = Depends(get_db),
           user = Depends(get_current_user)):
    preg: models.Pregunta = db.get(models.Pregunta, id)
    if preg.id_profesor != user.id_profesor:
        raise HTTPException(400, "Solo el autor la puede subir")
    if not preg:
        raise HTTPException(404, "No encontrado")
    if preg.estado != "borrador":
        raise HTTPException(400, "Solo borradores")
    preg.estado = "en revisión"; db.commit()
    enqueue_image_generation(background, id, preg.enunciado)
    return {"msg": "Enviado a revisión; la imagen se está generando."}

@router.post("/{id:int}/decision")
def decision(id: int,
             payload: schemas.DecisionCreate,
             db: Session = Depends(get_db),
             user = Depends(get_current_user)):
    preg = db.get(models.Pregunta, id)
    if not preg:
        raise HTTPException(404)
    if preg.estado not in ("en revisión",):
        raise HTTPException(400, "No está en revisión")
    if preg.id_profesor == user.id_profesor:
        raise HTTPException(403, "No puedes revisar tu propia pregunta")
    
    return crud_decision.create_decision(db, id, user.id_profesor, payload)

@router.post("/batch/decision", dependencies=[Depends(is_admin)])
def batch_decision(
    payload: BatchDecision,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    processed = 0
    for pid in payload.ids:
        preg = db.get(models.Pregunta, pid)
        if preg and preg.estado == "en revisión":
            crud_decision.create_decision(db, pid, user.id_profesor, payload)
            processed += 1
    return {"procesadas": processed}
