# tests/test_db.py
import pytest
from sqlalchemy import text
from app.database import engine

def test_db_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    assert result == 1
