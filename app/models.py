"""
Todas las tablas SQLAlchemy reflejan exactamente la BD mostrada.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Enum,
    ForeignKey, Table, SmallInteger
)
from sqlalchemy.orm import relationship

from .database import Base

# ——— Tabla puente ————————————————————————————————————————
Pregunta_Tema = Table(
    "pregunta_tema",
    Base.metadata,
    Column("id_pregunta", Integer, ForeignKey("pregunta.id_pregunta", ondelete="CASCADE"), primary_key=True),
    Column("id_tema",     Integer, ForeignKey("tema.id_tema",     ondelete="CASCADE"), primary_key=True),
)

# ——— Catálogos ————————————————————————————————————————————
class Isla(Base):
    __tablename__ = "isla"
    id_isla     = Column(SmallInteger, primary_key=True)
    nombre      = Column(String(80), nullable=False)
    descripcion = Column(Text)

    # Relación a la clase Pregunta
    preguntas   = relationship("Pregunta", back_populates="isla", cascade="all, delete-orphan")

class Tema(Base):
    __tablename__ = "tema"
    id_tema     = Column(Integer, primary_key=True)
    nombre      = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)

    # Relación many-to-many con la clase Pregunta
    preguntas   = relationship(
        "Pregunta",
        secondary=Pregunta_Tema,
        back_populates="temas"
    )

# ——— Profesores ————————————————————————————————————————
class Profesor(Base):
    __tablename__ = "profesor"
    id_profesor = Column(Integer, primary_key=True)
    nombre      = Column(String(50), nullable=False)
    apellido    = Column(String(50), nullable=False)
    correo      = Column(String(100), nullable=False, unique=True)
    pwd         = Column(String(255), nullable=False)
    rol         = Column(Enum("autor", "admin"), default="autor")
    activo      = Column(Boolean, default=True)
    campus      = Column(String(80))
    titulo      = Column(String(120))
    cargo       = Column(String(120))
    bio         = Column(Text)
    avatar_url  = Column(String(200))

    # Relaciones
    decisiones = relationship("Decision", back_populates="profesor")
    opciones   = relationship("Opcion",    back_populates="profesor")
    preguntas  = relationship("Pregunta",  back_populates="profesor")

# ——— Pregunta, Opción y Decisión ——————————————————————————————————
class Pregunta(Base):
    __tablename__ = "pregunta"
    id_pregunta    = Column(Integer, primary_key=True)
    enunciado      = Column(Text)
    tipo           = Column(Enum("abc", "vf", "checkbox"), default="abc", nullable=False)
    id_isla        = Column(SmallInteger, ForeignKey("isla.id_isla"), nullable=False)
    dificultad     = Column(SmallInteger, default=1, nullable=False)
    randomizar     = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    estado         = Column(Enum("borrador", "en revisión", "publicada", "rechazada"), default="borrador")
    url_imagen     = Column(String(200))
    id_profesor    = Column(Integer, ForeignKey("profesor.id_profesor"))

    # Relaciones
    isla       = relationship("Isla",     back_populates="preguntas")
    profesor   = relationship("Profesor", back_populates="preguntas")
    opciones   = relationship("Opcion",   back_populates="pregunta",   cascade="all, delete-orphan")
    decisiones = relationship("Decision", back_populates="pregunta",   cascade="all, delete-orphan")
    temas      = relationship(
        "Tema",
        secondary=Pregunta_Tema,
        back_populates="preguntas"
    )

class Opcion(Base):
    __tablename__ = "opcion"
    id_opcion      = Column(Integer, primary_key=True)
    id_pregunta    = Column(Integer, ForeignKey("pregunta.id_pregunta", ondelete="CASCADE"), nullable=False)
    texto          = Column(Text)
    url_imagen     = Column(String(200))
    fecha_creacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    id_profesor    = Column(Integer, ForeignKey("profesor.id_profesor"))
    es_correcta    = Column(Boolean, default=False)

    # Relaciones
    pregunta = relationship("Pregunta", back_populates="opciones")
    profesor = relationship("Profesor", back_populates="opciones")

class Decision(Base):
    __tablename__ = "decision"
    id_revision = Column(Integer, primary_key=True)
    id_pregunta = Column(Integer, ForeignKey("pregunta.id_pregunta", ondelete="CASCADE"), nullable=False)
    id_profesor = Column(Integer, ForeignKey("profesor.id_profesor"), nullable=False)
    fecha       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    decision    = Column(Enum("publicada", "rechazada"), nullable=False)
    comentario  = Column(Text)

    # Relaciones
    pregunta = relationship("Pregunta", back_populates="decisiones")
    profesor = relationship("Profesor", back_populates="decisiones")
