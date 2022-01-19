from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    aud: str
    exp: datetime
    jti: UUID