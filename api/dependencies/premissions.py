from fastapi import Depends, HTTPException, status

import models
from api.dependencies.get_user import access_token_required, GetUser


async def match_current_user(
    public_id: str,
    token: str = Depends(access_token_required)
) -> models.User:
    token_obj = GetUser(token, 'access')
    user = await token_obj.get_current_user()
    if(public_id != user.public_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cant access this user.'
        )
    return user