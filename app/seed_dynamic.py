#!/usr/bin/env python3
"""
seed_dynamic.py

Puebla la BD con datos de prueba, garantizando rollback si
ocurre cualquier excepción durante la transacción.
"""

import random
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.models import Profesor, Pregunta, Opcion
from app.utils.hashing import get_password_hash

# — Parámetros —
NUM_AUTORES       = 8
NUM_PREGUNTAS     = 40
OPCIONES_POR_PREG = 4
DEFAULT_PWD       = "demo123"
TEMA_IDS          = list(range(1, 11))  # IDs 1..10
FAKER_LOCALE      = "es_MX"

def main():
    fake = Faker(FAKER_LOCALE)
    db: Session = SessionLocal()

    try:
        # 0) Asegurar un admin - descomentar si se quiere incluir un admin fijo por defecto
        # admin = Profesor(
        #     nombre="Ada", apellido="Lovelace",
        #     correo="admin@demo.mx",
        #     pwd=get_password_hash("admin123"),
        #     rol="admin", activo=True,
        #     campus="Campus Centra", titulo="M.C."
        # )
        # db.merge(admin) # evita publicador
        # db.commit()

        # 1) Crear autores
        autores = []
        for _ in range(NUM_AUTORES):
            prof = Profesor(
                nombre   = fake.first_name(),
                apellido = fake.last_name(),
                correo   = fake.unique.email(),
                pwd      = get_password_hash(DEFAULT_PWD),
                rol      = "autor",
                activo   = True,
                campus   = fake.city(),
                titulo   = "M. C."
            )
            db.add(prof)
            autores.append(prof)
        db.commit()  # commit solo de los autores
        # refrescamos la lista con IDs
        for i, prof in enumerate(autores):
            autores[i] = db.get(Profesor, prof.id_profesor)

        # 2) Crear preguntas y opciones dentro de una sola transacción
        for _ in range(NUM_PREGUNTAS):
            autor = random.choice(autores)

            # 2.1) Pregunta
            preg = Pregunta(
                enunciado   = fake.sentence(nb_words=6).rstrip(".") + "?",
                tipo        = random.choice(["abc", "vf", "checkbox"]),
                id_isla     = random.randint(1, 10),
                dificultad  = random.randint(1, 3),
                randomizar  = bool(random.getrandbits(1)),
                id_profesor = autor.id_profesor,
                estado      = "borrador"
            )
            db.add(preg)
            db.flush()  # para obtener preg.id_pregunta

            # 2.2) Insertar temas en tabla puente
            temas = random.sample(TEMA_IDS, k=random.randint(1, 3))
            for tid in temas:
                db.execute(
                    text("""
                        INSERT IGNORE INTO pregunta_tema (id_pregunta, id_tema)
                        VALUES (:pid, :tid)
                    """),
                    {"pid": preg.id_pregunta, "tid": tid}
                )

            # 2.3) Opciones
            correct_idx = random.randrange(OPCIONES_POR_PREG)
            for idx in range(OPCIONES_POR_PREG):
                opt = Opcion(
                    id_pregunta = preg.id_pregunta,
                    texto       = fake.word(),
                    es_correcta = (idx == correct_idx),
                    id_profesor = autor.id_profesor
                )
                db.add(opt)

        # 3) Commit final de preguntas y opciones
        db.commit()
        print(f"✅ Pobladas {NUM_AUTORES} autores y {NUM_PREGUNTAS} preguntas demo.")

    except Exception as e:
        # En caso de cualquier error, deshacemos TODO lo hecho en esta sesión
        db.rollback()
        print("❌ Error durante el seed, se ha hecho rollback de la transacción.")
        raise

    finally:
        db.close()

if __name__ == "__main__":
    main()
