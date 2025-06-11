from app.models import Pregunta
from app.config import STATIC_DIR

def main(db=None):
    if db is None:
        # Solo producción: usa la función de dependencias para abrir sesión
        from app.database import get_db
        db = next(get_db())
        created_here = True
    else:
        created_here = False

    imgs = set(f.name for f in (STATIC_DIR / "preguntas").glob("*.png"))
    ids_validos = set(str(pid) + ".png" for (pid,) in db.query(Pregunta.id_pregunta).all())
    huérfanos = imgs - ids_validos
    for fname in huérfanos:
        (STATIC_DIR / "preguntas" / fname).unlink()
        print("Borrado:", fname)

    if created_here:
        db.close()

if __name__ == "__main__":
    main()
