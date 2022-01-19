import json
from datetime import timedelta

from fastapi import (
    APIRouter,
    Form,
    Depends,
    HTTPException,
    status,
    BackgroundTasks
)

import models, schemas, crud
from api.dependencies import premissions, get_user
from core.security import create_jwt_token, get_password, verify_password
from core.config import settings
from utils import util
from utils.sending_email import send_verification_email, send_reset_password_email
from utils.redis import redis

router = APIRouter(
    prefix='/user',
    tags=['User']
)


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(background_task: BackgroundTasks, user_in: schemas.UserCreate):
    user = await crud.user.read(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The user with this email already exists in the system.'
        )
    _id = await crud.user.create(user_in)

    token = create_jwt_token(str(_id), 'verification')
    background_task.add_task(
        send_verification_email,
        user_in.first_name,
        user_in.email,
        token
    )

    return {'detail': 'An email sent to your account, you have 5 minutes to verify.'}
    

@router.get('/{public_id}', response_model=schemas.UserOut)
async def read_user(user: models.User = Depends(premissions.match_current_user)):
    return user


@router.put('/{public_id}/update')
async def update_user(
    user_in: schemas.UserUpdate,
    user: models.User = Depends(premissions.match_current_user)
):
    user_in_dict = user_in.dict(exclude_none=True)
    if user_in_dict:
        await crud.user.update(user_in_dict, user.public_id)
        return {'detail': 'The user updated successfully.'}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='You must fill at least one field'
    )


@router.delete('/{public_id}/delete')
async def delete_user(
    public_id: str,
    token: str = Depends(get_user.refresh_token_required)
):
    token_obj = get_user.GetUser(token, 'refresh')
    user = await token_obj.get_current_user()
    if(public_id != str(user.public_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cant access this user.'
        )

    await redis.setex(
        str(token_obj.token_data.jti),
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        'true'
    )

    await crud.user.delete_by_id(public_id)

    return {'detail': 'The user deleted successfully.'}


@router.put('/{public_id}/reset-password')
async def reset_password(
    background_task: BackgroundTasks,
    old_password: str = Form(..., regex=settings.PASSWORD_REGEX),
    new_password: str = Form(..., regex=settings.PASSWORD_REGEX),
    user: models.User = Depends(premissions.match_current_user)
):  
    if new_password == old_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The new password must differ from the old password'
        )
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Wrong password'
        )
    
    await util.check_request_counter(user)
    
    token = create_jwt_token(user.public_id, 'verification')
    background_task.add_task(
        send_reset_password_email,
        user.first_name,
        user.email,
        user.public_id,
        token
    )
    await redis.setex(
        f'{user.public_id}_password',
        timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES),
        get_password(new_password)
    )
    del old_password, new_password

    return {'detail': 'An email sent to your account, you have 5 minutes to verify.'}


@router.get('/{public_id}/reset-password')
async def verify_reset_password(public_id: str, token: str):
    token_obj = get_user.GetUser(token, 'verification')
    user = await token_obj.get_current_user()
    if(public_id != user.public_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You cant access this user.'
        )

    new_password = await redis.get(f'{user.public_id}_password')

    await redis.setex(
        str(token_obj.token_data.jti),
        timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES),
        'true'
    )

    await crud.user.update(
        {'hashed_password': new_password},
        public_id
    )

    del new_password

    await redis.delete(f'{user.public_id}_current')
    await redis.delete(f'{user.public_id}_password')

    return {'detail': 'The password reset successfully.'}