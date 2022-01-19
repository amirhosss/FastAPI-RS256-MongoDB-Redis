from typing import Optional
from datetime import timedelta

from fastapi import HTTPException, status

import models
from core.config import settings
from .redis import redis


async def check_request_counter(
    user: models.User,
    limit: Optional[int] = settings.DEFAULT_LIMITATION
) -> None:
    if request_counter := await redis.get(f'{user.public_id}_counter'):
        if int(request_counter) > limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You cannot request this action, try one month later'
            )

        current_process = await redis.get(f'{user.public_id}_current')
        if current_process == 'true':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You should check your inbox, your email is still valid.'
            )

        await redis.set(
            f'{user.public_id}_counter',
            int(request_counter)+1,
            keepttl=True
        )
        await redis.setex(
            f'{user.public_id}_current',
            timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES),
            'true'
        )
    else:
        await redis.setex(
            f'{user.public_id}_counter',
            timedelta(days=30),
            1
        )
        await redis.setex(
            f'{user.public_id}_current',
            timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES),
            'true'
        ) 