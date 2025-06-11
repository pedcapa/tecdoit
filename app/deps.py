"""
Dependencias comunes: DB, usuario actual, rol admin.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from .database import get_db
from .models import Profesor
from .schemas import TokenData
from .config import SECRET_KEY, ALGORITHM

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Profesor:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales no válidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        data = TokenData(**payload)
    except (JWTError, ValueError):
        raise credentials_error
    user = db.get(Profesor, data.id_profesor)
    if not user or not user.activo:
        raise credentials_error
    return user

def is_admin(user: Profesor = Depends(get_current_user)):
    if user.rol != "admin":
        raise HTTPException(403, "Solo administradores")
    return True
