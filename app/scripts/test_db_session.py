from sqlalchemy import text
from app.database import SessionLocal, get_db

db = SessionLocal()
try:
    r = db.execute(text("SHOW TABLES")).fetchall()
    print("Tablas:", r)
finally:
    db.close()

# 2) Simular get_db como dependencia
gen = get_db()
db2 = next(gen)
print("Session OK:", db2)
db2.close()
try:
    next(gen)
except StopIteration:
    print("get_db cerró la sesión correctamente")
