"""
Tarea background que genera la imagen definitiva.
Se usa con FastAPI BackgroundTasks; si mañana escalas, cambia
por Celery.
"""
from fastapi import BackgroundTasks

from ..services.image_service import persist_image_and_update

def enqueue_image_generation(
    background: BackgroundTasks, id_pregunta: int, texto: str
):
    background.add_task(persist_image_and_update, id_pregunta, texto)
