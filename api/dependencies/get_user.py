from typing import Optional

from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic.error_wrappers import ValidationError
from jose import jwt
from jose.exceptions import JWTError

import crud, models, schemas
from core.config import settings
from core.security import public_key
from utils.redis import redis

security = HTTPBearer(auto_error=settings.HTTP_BEARER_AUTO_ERROR)


class TokenRequired:
    def __init__(self, token_type) -> None:
        self.token_type = token_type

    def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        access_token: Optional[str] = Cookie(None),
        refresh_token: Optional[str] = Cookie(None)

    ) -> Optional[str]:
        if credentials:
            return (token := credentials.credentials)
        elif access_token and self.token_type == 'access':
            return (token := access_token)
        elif refresh_token and self.token_type == 'refresh':
            return (token := refresh_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'}
        )


access_token_required = TokenRequired(token_type='access')
refresh_token_required = TokenRequired(token_type='refresh')


class GetUser:
    def __init__(self, token: str, audience: str) -> None:
        self.token = token
        self.audience = audience

    async def decode(self) -> None:
        try:
            payload = jwt.decode(
                self.token,
                public_key,
                algorithms=[settings.JWT_TOKEN_ALGORITHM],
                audience=self.audience
            )
            token_data = schemas.TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Could not validate credentials'
            )

        jti_status = await redis.get(str(token_data.jti))
        if jti_status and jti_status == 'true':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Token is invalidated'
            )

        self.token_data = token_data

    async def get_current_user(self) -> models.User:
        await self.decode()
        user = await crud.user.read_by_id(self.token_data.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        return user
 