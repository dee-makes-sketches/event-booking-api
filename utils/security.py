from pwdlib import PasswordHash
import jwt
from datetime import timedelta, datetime, UTC
from core.config import settings
#.recommended() defaults to Argon2 with secure, modern parameters
password_hash = PasswordHash.recommended()

#hash incoming password
def hash_password(password:str) -> str:
    return password_hash.hash(password)

#verify if incoming password matches with its hashed version
def verify_password(plain_password:str, hashed_password:str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


#create access token
def create_access_token(data:dict, expire_delta:timedelta | None = None) ->str:
    """
    take user's id from the data dict
    add expiration time
    sign it with server's secret key"""
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(UTC) + expire_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, settings.secret_key.get_secret_value(), settings.algorithm)

    return encode_jwt


def verify_access_token(token:str)->str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require":["exp", "sub"]}
        )
    except (jwt.InvalidTokenError, ValueError):
        return None
    else:
        return payload.get("sub")
