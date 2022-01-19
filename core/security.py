import uuid
from datetime import datetime, timedelta

from jose import jwt
from passlib.hash import bcrypt_sha256

from .config import settings


def get_password(password):
    return bcrypt_sha256.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_sha256.verify(plain_password, hashed_password)


with open('core/private_key.pem', 'rb') as private_file:
    private_key = private_file.read()
with open('core/public_key.pem', 'rb') as public_file:
    public_key = public_file.read()
    

def create_jwt_token(sub: str, aud: str, expires_delta: timedelta = None):
    expires_delta_condition = {
        'refresh': timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        'access': timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        'verification': timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES)
    }

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + expires_delta_condition[aud]

    to_encode = {'sub': sub, 'aud': aud, 'exp': expire, 'jti': str(uuid.uuid4())}
    encoded_jwt = jwt.encode(
        to_encode,
        private_key,
        algorithm=settings.JWT_TOKEN_ALGORITHM
    )
    return encoded_jwt
    