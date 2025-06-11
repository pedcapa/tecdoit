"""JWT helpers."""
from datetime import datetime, timedelta, timezone
from jose import jwt

from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MIN

def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    # Usar ahora con zona UTC explícita
    ahora = datetime.now(timezone.utc)
    expire = ahora + timedelta(
        minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MIN
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)