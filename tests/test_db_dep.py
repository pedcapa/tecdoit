from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal

def test_get_db_transaction(engine):
    # Creamos la app tal cual, usando get_db original
    app = FastAPI()

    @app.post("/boom")
    def boom(db: Session = Depends(get_db)):
        # Inserta un registro en test_rb
        db.execute(text("INSERT INTO test_rb () VALUES ()"))
        # Lanzamos excepción no-SQLAlchemy → get_db hará rollback
        raise HTTPException(400, "error")

    client = TestClient(app)
    resp = client.post("/boom")
    assert resp.status_code == 400

    # Ahora abrimos una NUEVA sesión para consultar el estado en BD
    session = SessionLocal()
    count = session.execute(text("SELECT COUNT(*) FROM test_rb")).scalar()
    session.close()
    assert count == 0, "La inserción debió revertirse"
