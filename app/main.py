from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import auth, islas, temas, profesores, preguntas, opciones, txt_to_img

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Administrador de Preguntas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(islas.router)
app.include_router(temas.router)
app.include_router(profesores.router)
app.include_router(preguntas.router)
app.include_router(opciones.router)
app.include_router(txt_to_img.router)

@app.get("/ping")
def ping(): return {"status": "ok"}
