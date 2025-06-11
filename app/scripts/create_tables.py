# antes de esto correr mysql -u root -e 'CREATE DATABASE IF NOT EXISTS TESTEO;'

from app.database import engine, Base
import app.models    # se asegura de registrar todos los modelos

Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas correctamente")