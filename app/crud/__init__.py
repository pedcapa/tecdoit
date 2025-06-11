"""Reexporta los submódulos CRUD para uso cómodo.

Ejemplo:
    from app import crud
    crud.preguntas.create_pregunta(...)
"""
from . import (
    isla,
    tema,
    profesor,
    preguntas,
    opciones,
    decisiones,
)
