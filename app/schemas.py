"""
Modelos Pydantic de entrada / salida.
Usando Pydantic v2: ConfigDict(from_attributes=True) en modelos de salida.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator

# ——— Auth ——————————————————————————————————————————————
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    id_profesor: int
    rol: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

# ——— Profesor ———————————————————————————————————————————
class ProfesorBase(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    campus: Optional[str] = None
    titulo: Optional[str] = None
    cargo: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfesorCreate(ProfesorBase):
    pwd: str
    rol: str = "autor"

class ProfesorOut(ProfesorBase):
    id_profesor: int
    rol: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)

# ——— Tema & Isla ——————————————————————————————————————
class IslaOut(BaseModel):
    id_isla: int
    nombre: str
    descripcion: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class TemaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class TemaOut(BaseModel):
    id_tema: int
    nombre: str
    descripcion: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

# ——— Opción ——————————————————————————————————————————
class OpcionCreate(BaseModel):
    texto: Optional[str]
    es_correcta: bool = False

class OpcionOut(BaseModel):
    id_opcion: int
    texto: Optional[str]
    url_imagen: Optional[str]
    es_correcta: bool
    
    model_config = ConfigDict(from_attributes=True)

# ——— Pregunta ——————————————————————————————————————
class PreguntaCreate(BaseModel):
    enunciado: str
    tipo: str = Field(..., pattern="^(abc|vf|checkbox)$")
    id_isla: int
    dificultad: int = Field(..., ge=1, le=3)
    randomizar: bool = False
    temas: List[int] = []

    opciones: List[OpcionCreate] = Field(
        ..., min_length=2, description="Debe haber al menos dos opciones"
    )

    @model_validator(mode="after")
    def check_opciones_por_tipo(self):
        total = len(self.opciones)
        correctas = sum(1 for o in self.opciones if o.es_correcta)

        if self.tipo == "vf":
            if total != 2:
                raise ValueError("Para Verdadero/Falso debe haber exactamente 2 opciones")
            if correctas != 1:
                raise ValueError("Para Verdadero/Falso debe marcarse 1 opción correcta")

        elif self.tipo == "abc":
            # min_items=2 ya asegura >=2; aquí forzamos exactamente 1 correcta
            if correctas != 1:
                raise ValueError("Para opción múltiple (ABC) debe marcarse exactamente 1 opción correcta")

        elif self.tipo == "checkbox":
            # min_items=2 ya asegura >=2
            if correctas < 1:
                raise ValueError("Para selección múltiple debe haber al menos 1 opción correcta")
            if correctas == total:
                raise ValueError("Para selección múltiple debe haber al menos 1 opción incorrecta")

        return self

class PreguntaOut(BaseModel):
    id_pregunta: int
    enunciado: str
    tipo: str
    id_isla: int
    dificultad: int
    randomizar: bool
    fecha_creacion: datetime
    estado: str
    url_imagen: Optional[str]
    id_profesor: int
    temas: List[TemaOut] = []
    opciones: List[OpcionOut] = []
    
    model_config = ConfigDict(from_attributes=True)

# ——— Decisiones ————————————————————————————————
class DecisionCreate(BaseModel):
    decision: str
    comentario: Optional[str]

# ——— Vista previa de imagen ————————————————————————————
class PreviewIn(BaseModel):
    enunciado: str
