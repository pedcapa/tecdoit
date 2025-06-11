"""
Variables globales tomadas de .env (python-dotenv).
Las rutas y TTLs se centralizan aquí para usarlas en todos los módulos.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(os.getenv("IMAGE_ROOT", "/var/www/preguntas-img"))
PREVIEW_DIR = Path("/tmp/previews")
PREVIEW_TTL = int(os.getenv("PREVIEW_TTL", "600"))
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")
SECRET_KEY = os.getenv("SECRET_KEY", "insecure-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 30
BASE_URL = os.getenv("BASE_URL", "http://localhost")